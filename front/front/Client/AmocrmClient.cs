using System.Net.Http.Headers;
using System.Text.Json;

public class AmocrmClient
{
    private readonly HttpClient _httpClient;
    private readonly IConfiguration _config;

    public AmocrmClient(HttpClient httpClient, IConfiguration config)
    {
        _httpClient = httpClient;
        _config = config;
    }

    private async Task<string> GetAccessTokenAsync()
    {
        return _config["Amocrm:AccessToken"]!;
    }

    public async Task<int?> FindContactByPhoneAsync(string phone)
    {
        var token = await GetAccessTokenAsync();
        _httpClient.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Bearer", token);
        var domain = _config["Amocrm:Domain"];
        var url = $"https://{domain}/api/v4/contacts?query={phone}";
        var response = await _httpClient.GetAsync(url);
        var content = await response.Content.ReadAsStringAsync();

        using var doc = JsonDocument.Parse(content);
        var root = doc.RootElement;
        if (root.TryGetProperty("_embedded", out var embedded) &&
            embedded.TryGetProperty("contacts", out var contacts) &&
            contacts.GetArrayLength() > 0)
        {
            return contacts[0].GetProperty("id").GetInt32();
        }

        return null;
    }

    public async Task<int> CreateContactAsync(string phone)
    {
        var token = await GetAccessTokenAsync();
        _httpClient.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Bearer", token);
        var domain = _config["Amocrm:Domain"];

        var contact = new
        {
            name = $"Контакт {phone}",
            custom_fields_values = new[]
            {
                new
                {
                    field_code = "PHONE",
                    values = new[] { new { value = phone } }
                }
            }
        };

        var content = new StringContent(JsonSerializer.Serialize(new[] { contact }), System.Text.Encoding.UTF8,
            "application/json");
        var response = await _httpClient.PostAsync($"https://{domain}/api/v4/contacts", content);
        var resultContent = await response.Content.ReadAsStringAsync();
        var json = JsonDocument.Parse(resultContent);
        return json.RootElement[0].GetProperty("id").GetInt32();
    }

    public async Task AddCallNoteAsync(CallNote note)
    {
        var token = await GetAccessTokenAsync();
        _httpClient.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Bearer", token);
        var domain = _config["Amocrm:Domain"];

        var content = new StringContent(JsonSerializer.Serialize(new[] { note }), System.Text.Encoding.UTF8,
            "application/json");
        var response = await _httpClient.PostAsync($"https://{domain}/api/v4/contacts/{note.EntityId}/notes", content);
        response.EnsureSuccessStatusCode();
    }
}