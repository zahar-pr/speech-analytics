using System.Net.Http.Headers;
using System.Text.Json;

public class TelfinClient
{
    private readonly HttpClient _httpClient;
    private readonly IConfiguration _config;

    public TelfinClient(HttpClient httpClient, IConfiguration config)
    {
        _httpClient = httpClient;
        _config = config;
    }

    private async Task<string> GetAccessTokenAsync()
    {
        return _config["Telfin:AccessToken"];
    }

    public async Task<TelfinCallDto> GetCallDetailsAsync(string callId)
    {
        var token = await GetAccessTokenAsync();
        _httpClient.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Bearer", token);
            
        var url = $"https://api.telphin.ru/calls/{callId}";
        var response = await _httpClient.GetAsync(url);
        var content = await response.Content.ReadAsStringAsync();
        var callData = JsonSerializer.Deserialize<TelfinCallDto>(content);
            
        return callData;
    }
}