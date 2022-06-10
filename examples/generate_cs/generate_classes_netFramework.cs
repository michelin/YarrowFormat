// https://www.nuget.org/packages/NJsonSchema.CodeGeneration.CSharp/
using NJsonSchema;
using NJsonSchema.CodeGeneration.CSharp;
using System;
using System.IO;
using System.Threading.Tasks;

namespace Generate_class_framework
{
    class Program
    {
        /// <summary>
        /// Generate .cs file which contains Yarrow c# class. 
        /// </summary>
        /// <param name="schemaPath">Path to the Yarrow schema JSON file.</param>
        /// <param name="generatedYarrowFilePath">Path to the generated .cs yarrow file</param>
        /// <param name="ns">Yarrow classes namespace</param>
        /// <returns></returns>
        static async Task GenerateJsonToCsAsync(string schemaPath, string generatedYarrowFilePath, string ns)
        {
            var jsonSchema = await JsonSchema.FromFileAsync(schemaPath);

            // GenerateNullableReferenceTypes must be set to false, not supported in .NET Framework
            var generatorSettings = new CSharpGeneratorSettings
            {
                Namespace = ns,
                GenerateOptionalPropertiesAsNullable = true,
                GenerateNullableReferenceTypes = false
            };

            var generator = new CSharpGenerator(jsonSchema, generatorSettings);

            var generatedFile = generator.GenerateFile();

            File.WriteAllText(generatedYarrowFilePath, generatedFile);
            Console.WriteLine("Code has been successfully generated.");
        }


        static void Main(string[] args)
        {
            // Path to schema Yarrow format JSON file.
            var schemaPath = $@"SchemaPath\yarrow_schema.json";

            // Yarrow namespace
            var ns = "YarrowLib.Domain";

            // Path to the .cs file generate with yarrow c# class.
            var generatedYarrowFilePath = Path.Combine(Directory.GetParent(Environment.CurrentDirectory).Parent.FullName, "YarrowSchema.g.cs");

            var t = Task.Run(async () =>
            {
                await GenerateJsonToCsAsync(schemaPath, generatedYarrowFilePath, ns);
            });

            t.Wait();
        }
    }
}
