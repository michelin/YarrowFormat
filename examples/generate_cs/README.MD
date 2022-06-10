# How to generate C# classes from a format json schema

## Requirements

* ```NJsonSchema 10.5.2 ```
* ```NJsonSchema.CodeGeneration.CSharp 10.5.2``` 

**_NOTE:_** In .Net Framework you may need ```System.ComponentModel.Annotations 5.0.0```

Tested with Application Console .Net Core 3.1 & .Net Framework 4.6.2

## Step 1

Get the [yarrow schema](/schema/yarrow_schema.json) and save it locally

## Step 2

Copy the [generate_classes_netCore.cs](/examples/generate_cs/generate_classes_netCore.cs) for .Net Core or [generate_classes_netFramework.cs](/examples/generate_cs/generate_classes_netFramework.cs) for .Net Framework and change the parameters :

* filePath : where to create the `YarrowSchema.g.cs` file
* ns : the namespace of the created classes

:warning: If you are using a C# version < 8, you need to remove option `GenerateNullableReferenceTypes = true` line 19

## Step 3

Fill the YarrowFormat and save as json files following these tutorials :

* [Generate Simple](/examples/generate_simple) files containing only images
* [Generate Overlays](/examples/generate_overlays/generate_overlays.py), a file with images whose id's match which represents linked images where annotations apply to all matching images.
