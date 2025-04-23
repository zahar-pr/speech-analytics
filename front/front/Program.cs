

var builder = WebApplication.CreateBuilder(args);

builder.Services.AddControllers();
builder.Services.AddHttpClient<AmocrmClient>();
builder.Services.AddScoped<CallProcessor>();

var app = builder.Build();

app.MapControllers();
app.Run();