using System.Text.Json.Serialization;

public class TelfinCallRequest
{
    [JsonPropertyName("src")]
    public string Source { get; set; }

    [JsonPropertyName("dst")]
    public string Destination { get; set; }

    [JsonPropertyName("caller_id")]
    public string CallerId { get; set; } 
}