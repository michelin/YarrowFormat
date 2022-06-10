using Newtonsoft.Json;
using System;
using System.Collections.Generic;
using System.IO;
using System.Threading.Tasks; 

// Namespace of the generated Yarrow c# classes
using YarrowLib.Domain;

namespace Generate_class_framework
{
    class Program
    {
        static void Main(string[] args)
        {
            Info info = new Info()
            {
                Source = "Demo",
                Date_created = DateTime.Now
            };

            YarrowDataset_pydantic yarrowDataset = new YarrowDataset_pydantic()
            {
                Info = info,
                Images = new List<Image_pydantic>() 
                {
                    new Image_pydantic()
                        {
                            Id = "1",
                            Width = 1000,
                            Height = 1000,
                            File_name = "test_image.jpg",
                            Date_captured = DateTime.Now,
                            Azure_url = "https://picsum.photos/200/300"
                        }
                }
            };

            try
            {
                string output = JsonConvert.SerializeObject(yarrowDataset);
                Console.WriteLine($"Serialization succeded : \n {output}");

                File.WriteAllText("examples/generate_simple/example_simple.json", output);
            }
            catch (Exception e)
            {
                Console.WriteLine(e);
            }
        }
    }
}
