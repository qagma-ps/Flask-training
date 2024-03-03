import random
import uuid
from pathlib import Path

import cv2
import numpy as np
import torch
import torchvision
from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    send_from_directory,
    url_for,
)
from flask_login import current_user, login_required
from PIL import Image
from sqlalchemy.exc import SQLAlchemyError

from apps.app import db
from apps.crud.models import User
from apps.detector.forms import DeleteForm, DetectorForm, UploadImageForm
from apps.detector.models import UserImage, UserImageTag

# Specify template_folter ( but not static )
dt = Blueprint("detector", __name__, template_folder="templates")


# colorize border color
def make_color(labels):
    colors = [[random.randint(0, 255) for _ in range(3)] for _ in labels]
    color = random.choice(colors)
    return color


def make_line(result_image):
    line = round(0.002 * max(result_image.shape[0:2])) + 1
    return line


def draw_lines(c1, c2, result_image, line, color):
    cv2.rectangle(result_image, c1, c2, color, thickness=line)
    return cv2


def draw_texts(result_image, line, c1, cv2, color, labels, label):
    display_txt = f"{labels[label]}"
    font = max(line - 1, 1)
    t_size = cv2.getTextSize(display_txt, 0, fontScale=line / 3, thickness=font)[0]
    c2 = c1[0] + t_size[0], c1[1] - t_size[1] - 3
    cv2.rectangle(result_image, c1, c2, color, -1)
    cv2.putText(
        result_image,
        display_txt,
        (c1[0], c1[1] - 2),
        0,
        line / 3,
        [255, 255, 255],
        thickness=font,
        lineType=cv2.LINE_AA,
    )
    return cv2


def exec_detect(target_image_path):
    # load label
    labels = current_app.config["LABELS"]
    # load image
    image = Image.open(target_image_path)
    # convert image data to tensor data
    image_tensor = torchvision.transforms.functional.to_tensor(image)

    # load studied model
    model = torch.load(Path(current_app.root_path, "detector", "model.pt"))
    # chage to model eval mode
    model = model.eval()
    # execute eval
    output = model([image_tensor])[0]

    tags = []
    result_image = np.array(image.copy())
    # add label to each object when model detected
    for box, label, score in zip(output["boxes"], output["labels"], output["scores"]):
        if score > 0.5 and labels[label] not in tags:
            # specify line color
            color = make_color(labels)
            # make line
            line = make_line(result_image)
            # specify location of line and label
            c1 = (int(box[0]), int(box[1]))
            c2 = (int(box[2]), int(box[3]))
            # add line to image
            cv2 = draw_lines(c1, c2, result_image, line, color)
            # add label to image
            cv2 = draw_texts(result_image, line, c1, cv2, color, labels, label)
            tags.append(labels[label])

    # generate image after detection
    detected_image_file_name = str(uuid.uuid4()) + ".jpg"

    # fetch location for image copy
    detected_image_file_path = str(
        Path(current_app.config["UPLOAD_FOLDER"], detected_image_file_name)
    )

    # Copy convert image file to the location
    cv2.imwrite(detected_image_file_path, cv2.cvtColor(result_image, cv2.COLOR_RGB2BGR))

    return tags, detected_image_file_name


def save_detected_image_tags(user_image, tags, detected_image_file_name):
    # store save location of processed image
    user_image.image_path = detected_image_file_name
    # make detetion flag True
    user_image.is_detected = True
    db.session.add(user_image)

    # make user_images_tags record
    for tag in tags:
        user_image_tag = UserImageTag(user_image_id=user_image.id, tag_name=tag)
        db.session.add(user_image_tag)

    db.session.commit()


# make endpoint using dt app
@dt.route("/")
def index():
    # Fetch image list by joing User and UserImage table
    user_images = (
        db.session.query(User, UserImage)
        .join(UserImage)
        .filter(User.id == UserImage.user_id)
        .all()
    )

    # fetch tag list
    user_image_tag_dict = {}
    for user_image in user_images:
        # fetch tag list for each images
        user_image_tags = (
            db.session.query(UserImageTag)
            .filter(UserImageTag.user_image_id == user_image.UserImage.id)
            .all()
        )
        user_image_tag_dict[user_image.UserImage.id] = user_image_tags

    # make instance of object detection form
    detector_form = DetectorForm()
    # make instance of object delete form
    delete_form = DeleteForm()

    return render_template(
        "detector/index.html",
        user_images=user_images,
        # pass tag list
        user_image_tag_dict=user_image_tag_dict,
        # pass object detection form
        detector_form=detector_form,
        # pass image delete form
        delete_form=delete_form,
    )


# make endpoint for image upload
@dt.route("/images/<path:filename>")
def image_file(filename):
    return send_from_directory(current_app.config["UPLOAD_FOLDER"], filename)


# upload path
@dt.route("/upload", methods=["GET", "POST"])
@login_required
def upload_image():
    # validation using UploadImageForm
    form = UploadImageForm()
    if form.validate_on_submit():
        # fetch uploaded image file
        file = form.image.data
        # retrieve file name and extension and convert file name to uuid
        ext = Path(file.filename).suffix
        print(ext)
        image_uuid_file_name = str(uuid.uuid4()) + ext
        print(image_uuid_file_name)
        # save file
        image_path = Path(current_app.config["UPLOAD_FOLDER"], image_uuid_file_name)
        file.save(image_path)

        # save to DB
        user_image = UserImage(user_id=current_user.id, image_path=image_uuid_file_name)
        db.session.add(user_image)
        db.session.commit()

        return redirect(url_for("detector.index"))
    return render_template("detector/upload.html", form=form)


#
@dt.route("/detect/<string:image_id>", methods=["POST"])
# login_required decorator added
@login_required
def detect(image_id):
    # fetch record from user_images table
    user_image = db.session.query(UserImage).filter(UserImage.id == image_id).first()
    if user_image is None:
        flash("物体検知対象の画像が存在しません。")
        return redirect(url_for("detector.index"))

    # fetch image file path for object detection
    target_image_path = Path(current_app.config["UPLOAD_FOLDER"], user_image.image_path)

    # get tags and image file path after object detection
    tags, detected_image_file_name = exec_detect(target_image_path)

    try:
        # store tags and image file path to db
        save_detected_image_tags(user_image, tags, detected_image_file_name)
    except SQLAlchemyError as e:
        flash("物体検知処理でエラーが発生しました。")
        # rollback
        db.session.rollback()
        # output error log
        current_app.logger.error(e)
        return redirect(url_for("detector.index"))

    return redirect(url_for("detector.index"))


@dt.route("/images/delete/<string:image_id>", methods=["POST"])
@login_required
def delete_image(image_id):
    try:
        # delete record from user_image_tags table
        db.session.query(UserImageTag).filter(
            UserImageTag.user_image_id == image_id
        ).delete()

        # delete record from user_images table
        db.session.query(UserImage).filter(UserImage.id == image_id).delete()

        db.session.commit()
    except SQLAlchemyError as e:
        flash("画像削除処理でエラーが発生しました。")
        # output error log
        current_app.logger.error(e)
        db.session.rollback()

    return redirect(url_for("detector.index"))


@dt.route("/images/search", methods=["GET"])
def search():
    # fetch list of images
    user_images = db.session.query(User, UserImage).join(
        UserImage, User.id == UserImage.user_id
    )

    # fetch search word out of GET parameter
    search_text = request.args.get("search")
    user_image_tag_dict = {}
    filtered_user_images = []

    # search tag associated with user_images by looping user_images
    for user_image in user_images:
        # fetch all tags if now keyword is specified
        if not search_text:
            user_image_tags = (
                db.session.query(UserImageTag)
                .filter(UserImageTag.user_image_id == user_image.UserImage.id)
                .all()
            )
        else:
            user_image_tags = (
                db.session.query(UserImageTag)
                .filter(UserImageTag.user_image_id == user_image.UserImage.id)
                .filter(UserImageTag.tag_name.like("%" + search_text + "%"))
                .all()
            )

            # do not return image if no tag is found
            if not user_image_tags:
                continue
            # fetch tag again if tags remain
            user_image_tags = (
                db.session.query(UserImageTag)
                .filter(UserImageTag.user_image_id == user_image.UserImage.id)
                .all()
            )

        # set tags to dictionary which key as user_image_id
        user_image_tag_dict[user_image.UserImage.id] = user_image_tags

        # set image info matrix of filtered result
        filtered_user_images.append(user_image)

    delete_form = DeleteForm()
    detector_form = DetectorForm()

    return render_template(
        "detector/index.html",
        user_images=filtered_user_images,
        user_image_tag_dict=user_image_tag_dict,
        delete_form=delete_form,
        detector_form=detector_form,
    )
