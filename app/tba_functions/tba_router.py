from fastapi import APIRouter, HTTPException

from ..utils.tba_communicator import tba_request

router = APIRouter()

@router.get("/raw/{tba_endpoint}")
async def get_tba_endpoint(tba_endpoint: str):
    return await tba_request(tba_endpoint)

@router.get("/match_schedule/{event_key}")
async def get_match_schedule(event_key: str):

    matches = await tba_request(f"event/{event_key}/matches/simple")

    if not matches:
        raise HTTPException(status_code=404, detail="Event not found")
    
    matches = [match for match in matches if match["comp_level"] == "qm"] # Only get qualification matches

    match_schedule_dict = {}
    for match in matches:
        match_key = match["key"].split("_qm")[1]
        team_dicts = []
        for alliance in ["blue", "red"]:
            teams = match["alliances"][alliance]["team_keys"]
            teams = [{"number": str(team[3:]), "color": alliance} for team in teams]
            team_dicts.extend(teams)
        match_schedule_dict[match_key] = {"teams": team_dicts}
    
    return match_schedule_dict

@router.get("/team_list/{event_key}")
async def get_team_list(event_key: str):
    raw_teams = await tba_request(f"event/{event_key}/teams/keys")
    if not raw_teams:
        raise HTTPException(status_code=404, detail="Event not found")
    team_list = [team[3:] for team in raw_teams]
    return team_list