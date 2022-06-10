from yarrow import rand_category, rand_contrib, rand_image


def test_cat_hash():
    cat1 = rand_category()
    cat2 = rand_category()
    cat_dict = {cat1: "cat1", cat2: "cat2"}
    assert cat_dict[cat1] == "cat1"
    assert cat_dict[cat2] == "cat2"


def test_contrib_hash():
    contrib1 = rand_contrib()
    contrib2 = rand_contrib()
    contrib_dict = {contrib1: "contrib1", contrib2: "contrib2"}

    assert contrib_dict[contrib1] == "contrib1"
    assert contrib_dict[contrib2] == "contrib2"


def test_image_hash():
    image1 = rand_image()
    image2 = rand_image()
    image_dict = {image1: "image1", image2: "image2"}

    assert image_dict[image1] == "image1"
    assert image_dict[image2] == "image2"
