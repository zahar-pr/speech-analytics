using System.Net.Http.Headers;
using System.Text;
using System.Text.Json;

namespace front.Domain.Service;

public class MakeCallService
{
    public async Task<bool> MakeCallAsync(string from, string to, TelfinOptions options, HttpClient httpClient,
        ILogger<TelfinProvider> logger)
    {
        var url = $"{options.BaseUrl}/api/v1/ext/callback";

        var request = new TelfinCallRequest
        {
            Source = from,
            Destination = to,
            CallerId = from
        };

        var httpRequest = new HttpRequestMessage(HttpMethod.Post, url)
        {
            Content = new StringContent(JsonSerializer.Serialize(request), Encoding.UTF8, "application/json")
        };

        httpRequest.Headers.Authorization = new AuthenticationHeaderValue("Bearer", options.AccessToken);

        try
        {
            var response = await httpClient.SendAsync(httpRequest);
            var responseContent = await response.Content.ReadAsStringAsync();

            if (!response.IsSuccessStatusCode)
            {
                logger.LogError("Telfin call failed: {StatusCode}, {Content}", response.StatusCode, responseContent);
                return false;
            }

            logger.LogInformation("Telfin call success: {Response}", responseContent);
            return true;
        }
        catch (Exception ex)
        {
            logger.LogError(ex, "Exception during Telfin call");
            return false;
        }
    }
}