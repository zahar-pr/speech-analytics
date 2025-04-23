using static ZadarmaWebhookDto;

public class CallProcessor
{
    private readonly AmocrmClient _amocrmClient;
    private readonly ZadarmaClient _zadarmaClient;

    public CallProcessor(AmocrmClient amocrmClient, ZadarmaClient zadarmaClient)
    {
        _amocrmClient = amocrmClient;
        _zadarmaClient = zadarmaClient;
    }

    public async Task ProcessCallAsync(ZadarmaWebhookDto dto)
    {
        if (dto.Event != "ended") return;

        var callDetails = await _zadarmaClient.GetCallDetailsAsync(dto.CallId);
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
