using System;
using System.Net.Http;
using System.Net.Http.Headers;
using System.Threading.Tasks;
using Newtonsoft.Json;
using System.Text;
using System.Collections.Generic;

namespace Integrations
{
    public class UISApiClient
    {
        private readonly HttpClient _httpClient;
        private readonly string _apiKey;
        private readonly string _baseUrl;

        public UISApiClient(string apiKey, string baseUrl = "https://dataapi.uiscom.ru/v2")
        {
            _httpClient = new HttpClient();
            _apiKey = apiKey;
            _baseUrl = baseUrl;
        }

        private async Task<T> RequestAsync<T>(HttpMethod method, string endpoint, Dictionary<string, string> queryParams = null)
        {
            var requestUrl = new StringBuilder($"{_baseUrl}{endpoint}");
            if (queryParams != null)
            {
                requestUrl.Append("?");
                foreach (var param in queryParams)
                {
                    requestUrl.Append($"{param.Key}={param.Value}&");
                }
                requestUrl.Length--; // remove last &
            }

            var request = new HttpRequestMessage(method, requestUrl.ToString());
            request.Headers.Authorization = new AuthenticationHeaderValue("Bearer", _apiKey);

            var response = await _httpClient.SendAsync(request);
            response.EnsureSuccessStatusCode();
            var json = await response.Content.ReadAsStringAsync();
            return JsonConvert.DeserializeObject<T>(json);
        }

        public async Task<CallsResponse> GetCallsAsync(string dateFrom, string dateTo, int limit = 100, int offset = 0)
        {
            var queryParams = new Dictionary<string, string>
            {
                { "date_from", dateFrom },
                { "date_to", dateTo },
                { "limit", limit.ToString() },
                { "offset", offset.ToString() }
            };

            return await RequestAsync<CallsResponse>(HttpMethod.Get, "/statistics/calls", queryParams);
        }

        public async Task<byte[]> DownloadRecordAsync(string recordUrl)
        {
            var response = await _httpClient.GetAsync(recordUrl);
            response.EnsureSuccessStatusCode();
            return await response.Content.ReadAsByteArrayAsync();
        }
    }

    public class CallsResponse
    {
        [JsonProperty("calls")]
        public List<CallRecord> Calls { get; set; }
    }

    public class CallRecord
    {
        [JsonProperty("id")]
        public string Id { get; set; }

        [JsonProperty("record_url")]
        public string RecordUrl { get; set; }
    }
}
