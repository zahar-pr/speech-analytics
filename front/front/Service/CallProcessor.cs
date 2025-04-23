
using System.Threading.Tasks;

namespace TelfinAmocrmIntegration.Services
{
    public class CallProcessor
    {
        private readonly AmocrmClient _amocrmClient;
        private readonly TelfinClient _telfinClient;

        public CallProcessor(AmocrmClient amocrmClient, TelfinClient telfinClient)
        {
            _amocrmClient = amocrmClient;
            _telfinClient = telfinClient;
        }

        public async Task ProcessCallAsync(TelfinWebhook dto)
        {
            if (dto.Event != "ended") return;

            var callDetails = await _telfinClient.GetCallDetailsAsync(dto.CallId);
            if (callDetails == null) return;

            var contactId = await _amocrmClient.FindContactByPhoneAsync(dto.Caller);
            if (contactId == null)
            {
                contactId = await _amocrmClient.CreateContactAsync(dto.Caller);
            }

            var note = new CallNote
            {
                EntityId = contactId.Value,
                Text = $"Звонок: {callDetails.Caller} → {callDetails.Callee}. Статус: {callDetails.Status}. Запись: {callDetails.RecordingUrl}",
                Phone = dto.Caller
            };

            await _amocrmClient.AddCallNoteAsync(note);
        }
    }
}