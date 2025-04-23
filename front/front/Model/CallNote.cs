public class CallNote
{
    public string NoteType { get; set; } = "call";
    public string Text { get; set; } = string.Empty;
    public int EntityId { get; set; }
    public string CallResult { get; set; } = "completed";
    public string CallStatus { get; set; } = "success";
    public string Phone { get; set; } = string.Empty;
}