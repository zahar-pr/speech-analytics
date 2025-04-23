public class ZadarmaCallDto
{
    public string CallId { get; set; }
    public string Caller { get; set; }
    public string Callee { get; set; }
    public DateTime StartTime { get; set; }
    public DateTime EndTime { get; set; }
    public string Status { get; set; }
    public string RecordingUrl { get; set; }
}