using System;
using System.Threading.Tasks;
using Adapters;

class Program
{
    static async Task Main(string[] args)
    {
        var adapter = new UISAdapter("api");

        var calls = await adapter.FetchCallsAsync("2025-04-01", "2025-04-26");//даты которые нужны

        foreach (var call in calls)
        {
            if (!string.IsNullOrEmpty(call.RecordUrl))
            {
                var savePath = $"records/{call.Id}.mp3";
                await adapter.DownloadRecordAsync(call.RecordUrl, savePath);
                Console.WriteLine($"Сохранена запись: {savePath}");
            }
        }
    }
}