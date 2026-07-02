"""The styled completion-email HTML (email-client-safe: table layout, inline
styles, web-safe fonts). This same _html() goes into apps/api/.../emails.py."""

def _html(link: str) -> str:
    return f"""\
<!doctype html><html><head><meta charset="utf-8"></head><body style="margin:0;padding:0;background:#FBF7F0;">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#FBF7F0;">
  <tr><td align="center" style="padding:32px 16px;">
    <table role="presentation" width="600" cellpadding="0" cellspacing="0" style="max-width:600px;width:100%;background:#FFFFFF;border:1px solid #ECE3D0;">
      <!-- header -->
      <tr><td style="padding:28px 40px 0 40px;">
        <div style="font-family:Arial,Helvetica,sans-serif;font-size:13px;letter-spacing:4px;color:#C25E37;font-weight:bold;">V Y K A</div>
      </td></tr>
      <tr><td style="padding:18px 40px 0 40px;"><div style="height:1px;background:#ECE3D0;line-height:1px;">&nbsp;</div></td></tr>
      <!-- body -->
      <tr><td style="padding:30px 40px 0 40px;">
        <h1 style="margin:0;font-family:Georgia,'Times New Roman',serif;font-weight:normal;font-size:30px;line-height:1.2;color:#15110D;">Camera ta e gata.</h1>
        <p style="margin:16px 0 0 0;font-family:Arial,Helvetica,sans-serif;font-size:16px;line-height:1.6;color:#332C24;">
          Designul tău — reimaginat cu mobilier real, gata de cumpărat — te așteaptă.
        </p>
      </td></tr>
      <!-- button (table cell = Outlook-safe) -->
      <tr><td style="padding:28px 40px 0 40px;">
        <table role="presentation" cellpadding="0" cellspacing="0"><tr>
          <td align="center" bgcolor="#C25E37" style="background:#C25E37;">
            <a href="{link}" style="display:inline-block;padding:14px 32px;font-family:Arial,Helvetica,sans-serif;font-size:15px;font-weight:bold;color:#FBF7F0;text-decoration:none;">Vezi designul&nbsp;&rarr;</a>
          </td>
        </tr></table>
      </td></tr>
      <tr><td style="padding:14px 40px 0 40px;">
        <p style="margin:0;font-family:Arial,Helvetica,sans-serif;font-size:13px;color:#6B6155;">Linkul e legat de contul tău Vyka.</p>
      </td></tr>
      <!-- footer -->
      <tr><td style="padding:30px 40px 28px 40px;">
        <div style="height:1px;background:#ECE3D0;line-height:1px;">&nbsp;</div>
        <p style="margin:18px 0 0 0;font-family:Arial,Helvetica,sans-serif;font-size:13px;line-height:1.6;color:#6B6155;">
          Camera ta, regândită cu mobilier real din magazine din România.<br>
          <a href="https://vyka.ro" style="color:#C25E37;text-decoration:none;">vyka.ro</a>
        </p>
        <p style="margin:12px 0 0 0;font-family:Arial,Helvetica,sans-serif;font-size:11px;line-height:1.5;color:#A89773;">
          SC Turist în Transilvania SRL · Mediaș, România
        </p>
      </td></tr>
    </table>
  </td></tr>
</table>
</body></html>"""

if __name__ == "__main__":
    import pathlib
    html = _html("https://vyka.ro/app/wizard/ee0fa358-eb03-4522-9039-f4b34cd2042d")
    out = pathlib.Path(__file__).resolve().parent.parent / "out" / "work" / "email_preview.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html)
    print("wrote", out)
