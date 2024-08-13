import requests
import asyncio
from fasthtml.common import *

def render(site):
    sid= f'site-{site.ROWID}'
    delete = A("Delete", hx_delete=f"/{site.ROWID}",hx_swap="outerHTML", target_id=f'{sid}')
    name_link = A(site.name, href=site.url, target="_blank")
    return Tr(Td(name_link), Td(site.tech), Td(site.service), Td(site.status), Td(site.touch), Td(delete), id=sid)

app, rt, sites, Site= fast_app("mysites.db", live=True, ROWID=int, name=str, tech=str, service=str, status=str, touch=bool, pk='ROWID', url=str, render=render)

def add_inputs(): return Input(placeholder="add new site", id="name", hx_swap_oob="true"), Input(placeholder="tech", id="tech", hx_swap_oob="true"), Input(placeholder="service", id="service", hx_swap_oob="true"), Input(placeholder="url", id="url", hx_swap_oob="true")

@rt("/")
def get():
    Socials(
            title="Deployment Dashboard",
            site_name="Deployment Dashboard",
            description="A tool to check Jack's Deployments",
            image="https://vercel.fyi/fasthtml-og",
            url="https://fasthtml-template.vercel.app",
        ),
    frm = Form (Group(add_inputs(), Button("Add") ),
        hx_post ="/", target_id="sites-table", hx_swap="beforeend"
    )
    table = Table(
    Thead(Tr(Th("Name"), Th("Tech"), Th("Service"), Th("Status"), Th("Touched"), Th("Delete?"))),
    Tbody(*sites(), id="sites-table"),
)
    return (Titled("Deployments Dashboard", Card(table, header=frm, footer=Footer())))


def Footer():
    return (
                    P(
                        A(
                            "View Code",
                            href="https://github.com/jones58/fasthtml-test",
                            target="_blank",
                        ),
                        )),

@rt("/{sid}")
def delete(sid: int): sites.delete(sid)


def check_url(url):
    try:
        response = requests.get(url, timeout=5)
        return response.status_code == 200
    except:
        return False

async def update_statuses():
    while True:
        for site in sites():
            site.status = "Up" if check_url(site.url) else "Down"
            sites.update(site)
        await asyncio.sleep(60)  # Check every minute

@rt("/")
def post (site: Site): # type: ignore
    if site.url and not site.url.startswith('https://'):
        site.url = 'https://' + site.url
    site.status = "Up" if check_url(site.url) else "Down"
    return sites.insert(site), add_inputs()

serve()
