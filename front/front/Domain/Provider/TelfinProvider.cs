using front.Domain.Service;
using Microsoft.Extensions.Options;

public class TelfinProvider(IOptions<TelfinOptions> options, ILogger<TelfinProvider> logger, HttpClient httpClient, 
    CallService callService)
    : ITelephonyProvider
{
    private readonly TelfinOptions options = options.Value;
    private readonly ILogger<TelfinProvider> logger = logger;
    private readonly HttpClient httpClient = httpClient;
    private readonly CallService callService;

    public async Task<bool> MakeCallAsync(string from, string to)
    {
        return await callService.MakeCallService.MakeCallAsync(from, to, options, httpClient, logger);
    }

    public async Task<bool> HangUpCallAsync(string callId)
    {
        logger.LogWarning("Telfin API does not support call termination via API. CallId={CallId}", callId);
        // Telfin API не поддерживает завершение вызова через публичные конечные точки HTTP.
        // Возможные альтернативы: Asterisk AMI или завершение сигнала через SIP (не реализовано).
        return false;
    }


    public async Task<string> GetCallStatusAsync(string callId)
    {
        return await callService.CallStatusService.GetCallStatusAsync(callId, options, httpClient, logger);
    }
}