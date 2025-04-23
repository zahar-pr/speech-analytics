public class ZadarmaWebhookDto
{
    public string CallId { get; set; } = string.Empty;
    public string Event { get; set; } = string.Empty;
    public string Caller { get; set; } = string.Empty;
    public string Callee { get; set; } = string.Empty;
    public DateTime Timestamp { get; set; }
    public string? RecordingUrl { get; set; }
}