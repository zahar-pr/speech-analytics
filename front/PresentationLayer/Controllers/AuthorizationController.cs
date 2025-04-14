using Microsoft.AspNetCore.Mvc;

namespace PresentationLayer.Controllers;

public class AuthorizationController: Controller
{
    public IActionResult Authorization()
    {
        return View();
    }
}