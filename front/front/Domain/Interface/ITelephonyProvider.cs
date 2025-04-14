public interface ITelephonyProvider
{
    Task<bool> MakeCallAsync(string from, string to);
    Task<bool> HangUpCallAsync(string callId);
    Task<string> GetCallStatusAsync(string callId);
}