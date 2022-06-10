// https://www.nuget.org/packages/NJsonSchema.CodeGeneration.CSharp/
using NJsonSchema.CodeGeneration.CSharp;
using NJsonSchema;

public class Program
{
  public static async Task Main()
  {
    // Le chemin auquel lequel le code généré sera sauvegardé
    var filePath = Path.Combine("src", "Yarrow", "YarrowLib", "Domain", "YarrowSchema.g.cs");
    var ns = "YarrowLib.Domain";
    // Chemin vers un fichier qui contient le schema JSON du format Yarrow. 
    var schemaPath = ;

    var jsonSchema = await JsonSchema.FromFileAsync(schemaPath);
    var generatorSettings = new CSharpGeneratorSettings
    {
        Namespace = ns,
        GenerateOptionalPropertiesAsNullable = true,
        GenerateNullableReferenceTypes = true
    };
    var generator = new CSharpGenerator(jsonSchema, generatorSettings);
    var generatedFile = generator.GenerateFile();
    await File.WriteAllTextAsync(filePath, generatedFile);
    Console.WriteLine("Code has been successfully generated.");
  }
}