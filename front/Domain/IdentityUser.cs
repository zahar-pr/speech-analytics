
using Microsoft.AspNetCore.Identity;

namespace Domain;

public class User : IdentityUser
{
    public string email { get; set; }
    public string login { get; set; }
}