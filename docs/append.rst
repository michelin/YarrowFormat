Merging Yarrows
===============

The YarrowDataset structure can be used both to describe a single image or multiple images that a part of the same dataset.

When constructing such dataset you may need to add multiple pre-existing Yarrows into an existing one or a new one, this document describes the possible ways to do this

Append another Yarrow into one
------------------------------

Given 2 existing YarrowDataset::

    yar_dataset1 = YarrowDataset(...)
    yar_dataset2 = YarrowDataset(...)

To add dataset 2 to dataset 1::

    yar_dataset1.append(yar_dataset2)

This will result in the following :

- ``yar_dataset2`` will be unchanged
- In ``yar_dataset1`` The ``Info`` property will be unchanged
- The ``images`` of ``yar_dataset2`` will be added to ``yar_dataset1`` only if they are not already present
    - The meta key is ignored when comparing two ``Image`` objects
- The ``contributors`` of ``yar_dataset2`` will be added to ``yar_dataset1`` only if they are not already present
- The ``annotations`` of ``yar_dataset2`` will be added to ``yar_dataset1`` only if they are not already present
    - The meta key is ignored when comparing two ``Annotation`` objects
    - If the images of a given ``annotation`` are already in ``yar_dataset1`` they are relinked to the ``yar_dataset1`` ones
    - The previous statement is also true for ``contributors`` and ``categories``

Extend a Yarrow with a list
---------------------------

Given multiple existing YarrowDataset::

    yar_dataset1 = YarrowDataset(...)
    yar_dataset_list = [YarrowDataset(...), YarrowDataset(...), ...]

You can extend the first one with the list using::

    yar_dataset1.extend(yar_dataset_list)

As a result all the Yarrows will be appended to the first one following the same rules as the ``append()`` function

To append only parts of a Yarrow
--------------------------------

If you want to append only a subset of a Yarrow or individual element you can use the following methods::

    info = Info(source="tutorial")
    yar_dataset1 = YarrowDataset(info=info, images=[])

    image1 = Image(...)

    yar_dataset1.add_image(image1) # To add a single image
    assert len(yar_dataset1.images) == 1
    yar_dataset1.add_images([image1]) # To add a list of images
    assert len(yar_dataset1.images) == 1 # as we already added image1, it won't be added a second time

    annotation1 = Annotation(images=[image1], ...)

    yar_dataset1.add_annotation(annotation1) # To add a single annotation
    assert len(yar_dataset1.images) == 1 # image1 was already present so it wasn't added

!!! A copy is made before appending objects !!! With the previous code::

    assert yar_dataset1.images[0] == image1 # They will be equal...
    assert yar_dataset1.image[0] is not image1 # But they won't be the same object

    assert yar_dataset1.annotations[0] == annotation1 # Same with annotation, they will be equal...
    assert yar_dataset1.annotations[0] is not annotation1 # But they won't be the same object
