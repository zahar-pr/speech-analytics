using System.Net.Http.Headers;
using System.Text.Json;

public class ZadarmaClient
{
    private readonly HttpClient _httpClient;
    private readonly IConfiguration _config;

    public ZadarmaClient(HttpClient httpClient, IConfiguration config)
    {
        _httpClient = httpClient;
        _config = config;
    }

    private async Task<string> GetAccessTokenAsync()
    {
        return _config["Zadarma:AccessToken"];
    }

    public async Task<ZadarmaCallDto> GetCallDetailsAsync(string callId)
    {
        var token = await GetAccessTokenAsync();
        _httpClient.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Bearer", token);
            
        var url = $"https://api.zadarma.com/v1/calls/{callId}";
        var response = await _httpClient.GetAsync(url);
        var content = await response.Content.ReadAsStringAsync();
        var callData = JsonSerializer.Deserialize<ZadarmaCallDto>(content);
            
        return callData;
    }
}