var builder = WebApplication.CreateBuilder(args);
var app = builder.Build();
builder.Services.Configure<TelfinOptions>(builder.Configuration.GetSection("Telephony:Telfin"));
builder.Services.AddHttpClient<TelfinProvider>();

app.MapGet("/", () => "Hello World!");

app.Run();
