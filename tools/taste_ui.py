from flask import Flask, render_template, request, redirect, url_for, jsonify
import uuid
import datetime
import os

from creative.reasoning.directions import ideate_directions
from creative.context import CustomerContext
from creative.reasoning.taste_ui_helper import save_taste_label

app = Flask(__name__, template_folder=os.path.join(os.path.dirname(__file__), "templates"))


@app.route("/", methods=["GET"])
def index():
    # lightweight context for sampling candidates
    ctx = CustomerContext(
        category="fashion",
        subcategory="streetwear",
        product_name="Sample Product",
        product_description="Short description",
        price="$99",
        brand_name="Sample",
        audience="young professionals",
        location="remote",
        language="en",
        visual_style="editorial",
    )

    candidates = ideate_directions(ctx, brief="Rate these", n=3)
    # prepare simple payload: list of concepts and short thesis
    choices = [
        {"id": str(i), "concept": c.direction.concept, "thesis": c.direction.visual_thesis}
        for i, c in enumerate(candidates)
    ]

    return render_template("taste_index.html", choices=choices)


@app.route("/submit", methods=["POST"])
def submit():
    chosen = request.form.get("chosen")
    other = request.form.getlist("other")
    note = request.form.get("note", "")

    record = {
        "id": str(uuid.uuid4()),
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "chosen": chosen,
        "other": other,
        "note": note,
    }

    path = save_taste_label(record)
    return redirect(url_for("index"))


@app.route("/healthz")
def healthz():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
