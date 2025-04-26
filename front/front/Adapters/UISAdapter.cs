
using Integrations;

namespace Adapters
{
    public class UISAdapter
    {
        private readonly UISApiClient _client;

        public UISAdapter(string apiKey)
        {
            _client = new UISApiClient(apiKey);
        }

        public async Task<List<CallRecord>> FetchCallsAsync(string dateFrom, string dateTo)
        {
            var allCalls = new List<CallRecord>();
            int offset = 0;
            const int limit = 100;

            while (true)
            {
                var response = await _client.GetCallsAsync(dateFrom, dateTo, limit, offset);
                if (response == null || response.Calls == null || response.Calls.Count == 0)
                    break;

                allCalls.AddRange(response.Calls);
                offset += response.Calls.Count;
            }

            return allCalls;
        }

        public async Task<string> DownloadRecordAsync(string recordUrl, string savePath)
        {
            var data = await _client.DownloadRecordAsync(recordUrl);
            var directory = Path.GetDirectoryName(savePath);
            if (!Directory.Exists(directory))
            {
                Directory.CreateDirectory(directory);
            }
            await File.WriteAllBytesAsync(savePath, data);
            return savePath;
        }
    }
}