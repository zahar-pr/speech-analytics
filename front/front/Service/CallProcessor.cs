public class CallProcessor
{
    private readonly AmocrmClient _amocrmClient;

    public CallProcessor(AmocrmClient amocrmClient)
    {
        _amocrmClient = amocrmClient;
    }

    public async Task ProcessCallAsync(TelfinWebhook dto)
    {
        if (dto.Event != "ended") return;

        var contactId = await _amocrmClient.FindContactByPhoneAsync(dto.Caller);
        if (contactId == null)
        {
            contactId = await _amocrmClient.CreateContactAsync(dto.Caller);
        }

        var note = new CallNote
        {
            EntityId = contactId.Value,
            Text = $"Звонок: {dto.Caller} → {dto.Callee}. Запись: {dto.RecordingUrl}",
            Phone = dto.Caller
        };

        await _amocrmClient.AddCallNoteAsync(note);
    }
}