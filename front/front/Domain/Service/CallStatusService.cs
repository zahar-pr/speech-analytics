using System.Net.Http.Headers;
using System.Text.Json;

namespace front.Domain.Service;

public class CallStatusService
{
    public async Task<string> GetCallStatusAsync(string callId, TelfinOptions options, HttpClient httpClient,
        ILogger<TelfinProvider> logger)
    {
        var url = $"{options.BaseUrl}/api/v1/ext/status?uuid={callId}";

        var httpRequest = new HttpRequestMessage(HttpMethod.Get, url);
        httpRequest.Headers.Authorization = new AuthenticationHeaderValue("Bearer", options.AccessToken);

        try
        {
            var response = await httpClient.SendAsync(httpRequest);
            var responseContent = await response.Content.ReadAsStringAsync();

            if (!response.IsSuccessStatusCode)
            {
                logger.LogError("Failed to get call status from Telfin: {StatusCode}, {Content}",
                    response.StatusCode, responseContent);
                return "Error: Failed to get status";
            }

            var callStatusResponse = JsonSerializer.Deserialize<JsonElement>(responseContent);
            var callStatus = callStatusResponse.GetProperty("call_status").GetString();

            logger.LogInformation("Call status from Telfin: {CallStatus}", callStatus);
            return callStatus;
        }
        catch (Exception ex)
        {
            logger.LogError(ex, "Exception while getting call status from Telfin");
            return "Error: Exception during request";
        }
    }
}