using Microsoft.AspNetCore.Mvc;

[ApiController]
[Route("api/webhook/telfin")]
public class WebhookController : ControllerBase
{
    private readonly CallProcessor _callProcessor;

    public WebhookController(CallProcessor callProcessor)
    {
        _callProcessor = callProcessor;
    }

    [HttpPost]
    public async Task<IActionResult> ReceiveCallEvent([FromBody] TelfinWebhook dto)
    {
        await _callProcessor.ProcessCallAsync(dto);
        return Ok();
    }
}