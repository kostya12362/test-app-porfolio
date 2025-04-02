import os

import openai
import json


class GPTParser:
    """
    A parser that uses the OpenAI API to extract structured location data from raw HTML or text.
    The input content is expected to contain multiple locations. The parser extracts the following fields:
    country, region, city, address, lat, lon
    """

    def __init__(self, content: str, openai_api_key: str, openai_org: str = None, model: str = "gpt-4"):
        self.content = content
        self.openai_api_key = openai_api_key
        self.openai_org = openai_org
        self.model = model
        self.fields = ["country", "region", "city", "address", "lat", "lon"]

        openai.api_key = self.openai_api_key
        if self.openai_org:
            openai.organization = self.openai_org

    def parse(self) -> dict:
        """
        Sends the content to the OpenAI API and returns a structured list of locations in a dictionary.
        Each location must include: country, region, city, address, lat, lon
        """

        function_schema = {
            "type": "object",
            "properties": {
                "data": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "country": {"type": "string"},
                            "region": {"type": "string"},
                            "city": {"type": "string"},
                            "address": {"type": "string"},
                            "lat": {"type": "number"},
                            "lon": {"type": "number"}
                        },
                        "required": self.fields
                    }
                }
            },
            "required": ["data"]
        }

        messages = [
            {
                "role": "system",
                "content": (
                    "You are a highly accurate geolocation data parser. "
                    "From the provided raw HTML or text, extract a list of all possible locations. "
                    "For each location, return the following fields: country, region, city, address, lat, lon. "
                    "Make sure to return an array under the key 'data' containing all found locations."
                )
            },
            {"role": "user", "content": self.content}
        ]

        functions = [{
            "name": "extract_locations",
            "description": "Extracts all available location data from the provided HTML or text.",
            "parameters": function_schema
        }]

        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=messages,
                functions=functions,
                function_call={"name": "extract_locations"}
            )
            arguments = response.choices[0].message.get("function_call", {}).get("arguments", "{}")
            parsed_result = json.loads(arguments)

            # Ensure 'data' is present and each location includes all required fields
            result = parsed_result.get("data", [])
            for loc in result:
                for field in self.fields:
                    loc.setdefault(field, "")

            return {"data": result}
        except Exception as e:
            print("Error during GPT parsing:", e)
            return {"data": []}


# Example usage
if __name__ == '__main__':
    from conf import API_KEY
    parser = GPTParser(
        content='''BIRMINGHAM is quickly transforming into a "third world city", according to residents impacted by the ongoing bin strikes which has left 17,000 tonnes of rubbish on the streets.

A major incident was declared this week by Birmingham City Council after the industrial action left mountains of uncollected waste piled high across the city.

Sign up for The Sun newsletter

Email address
Sign up
Your info will be used in accordance with our Privacy Policy

Pile of garbage bags on a residential street.
8
Rubbish piled up on Grove Cottage Rd in Bordesley Green in BirminghamCredit: SWNS
Two large rats near trash.
8
'Rats the size of cats' have been terrorising localsCredit: SelwynPics
Overfilled dumpsters overflowing with trash bags and cardboard boxes on a city street.
8
City residents claim they can smell the stench while walking down the streetCredit: Alamy
Members of the Unite union have been on all-out strike since March 11 in a dispute over pay and job losses.

Brummies say the row has left many areas looking like a "war zone" and a "third world country" and they now fear for their health.

Locals have previously reported "rats the size of cats" scurrying around their neighbourhoods while stray cats and foxes also tear open bags in search of food.

Shocking photos over the last few weeks have shown mountains of filthy fly-tipped rubbish and overflowing bin bags strewn across the second city.

READ MORE ABOUT THE BIN ISSUE

RUBBISH LOAD 'Major incident' declared in Birmingham as 17k TONNES of rubbish uncollected

RAT OUT OF HELL We live in seaside town infested with 'super-rats' - no one can stop them
The city's "rat man" - pest control expert Will Timms - said his phone is ringing off the hook.

The owner of WJ Pest Solutions is "absolutely shattered" after working non-stop for two-and-a-half months.

"There's a real sense of disbelief about the scale of what's happening here. I've been doing this for 11 years, and I've never seen anything like this," he told the i Paper.

"The rats are not only getting bigger, but they're also getting bolder, venturing into people's homes and even destroying cars."

Most read in The Sun
McFly star rushed to hospital after emergency leaves him 'looking smashed up'
HOSPITAL DASHMcFly star rushed to hospital after emergency leaves him 'looking smashed up'
Virginia Giuffre charged with breaching restraining order DAYS before crash
VIRGINIA CHARGEVirginia Giuffre charged with breaching restraining order DAYS before crash
Batman and Top Gun star Val Kilmer dies aged 65 after pneumonia battle
LEGEND LOSTBatman and Top Gun star Val Kilmer dies aged 65 after pneumonia battle
Watch Stacey Solomon confront son Zach, 17, in fiery row as he swears at her
family clashWatch Stacey Solomon confront son Zach, 17, in fiery row as he swears at her
Dad-of-two Emil Laursen, 34, of Balsall Heath, said bankrupt Birmingham was becoming a "joke" as the bin strike chaos continued.

He said: "We can't believe it has been allowed to get to this point, it has become a public health issue for sure.

Play Video
Up Next

Smugglers are 'offering VIP and first-class dinghies' for migrants wanting extra legroom
We’ve decked out our house for FREE using brand new furniture we found in bins
"We are fast transforming into a third world city. The place is becoming a joke. It had worked for years to shake off this label of being a dump.

"But just look at the streets now. It has literally become a makeshift dump. We're back to being laughing stock.

"We've seen some amazing community spirit with people helping to clear the mess but others have just dumped bags anywhere and everywhere.

"Some are taking no pride in the area and the affect has been these scenes of absolute carnage, like a war zone. The whole situation is a mess, quite literally."

Mazar Dad is a former senior manager at a Birmingham waste depot and now works for the charity Mecc Trust in Balsall Heath.

The 56-year-old said: "The problem has got tremendously worse week by week.

"The rat population has increased, you've got cats and foxes roaming the streets ripping open bags for food.

"It is just appalling there has been no adequate contingency plan put in place and now we have tonnes of waste on the streets.

"There's been all the talk of it costing millions in equal pay claims but nobody seems to be talking about how many millions it will cost just to clear the streets up.

"If the strikes ended tomorrow it would still take months and months to shift the rubbish caused by this fiasco.

"There's all sorts of implications, you've got the health issues as it gets warmer. You'll see even more rats. And then there's the economical impact on the city too.

"We have elected members and people in highly-paid jobs managing these services so it's disgraceful it's been allowed to come to this.

Large rat running across pavement.
8
Vermin the size of 'small cats' were seen scurrying around the streetsCredit: SelwynPics
Man walking past a large pile of garbage bags.
8
Waste collectors have vowed to extend strike action indefinitelyCredit: Alamy
Pile of garbage bags and shopping carts overflowing onto a residential street.
8
There is no sign of the dispute being resolvedCredit: LNP
"I ran a depot a few years ago and at the last strikes in 2017 the council put these new job roles in place but they have just been terribly mismanaged since.

"We definitely need central government intervention, I cannot believe it has been allowed to get to this stage."

Mumtaz Khadim, a butcher at Al Bodr supermarket in Balsall Heath, said: "I think it's ridiculous, somebody needs to come and pick this up.

"As a community we are all together as one but nobody is helping us out.

"It's no good for the health plus, we have children here going to school and they have to see all this. The situation is just no good for anybody."

Birmingham City Council said actions on the picket line had been blocking contingency vehicles from getting out of the depot to collect what rubbish they could.

They said a major incident needed to be declared following "rising concerns of risks to public health and damage to our environment".

Councillor John Cotton, leader of Birmingham City Council, said: "It's regrettable that we have had to take this step, but we cannot tolerate a situation that is causing harm and distress to communities across Birmingham.

"I respect the right to strike and protest, however actions on the picket line must be lawful and sadly the behaviour of some now means we are seeing a significant impact on residents and the city's environment.

"Unless we declare a major incident and deploy the waste service's contingency plan, then we would be unable to clear the backlog of waste on the streets or improve the frequency of collections.

Rats the size of cats roam the streets

By Tracey Kandohla & Freya ParsonsTHERE are rats the size of cats in this UK city and mountains of rubbish along the streets.Residents have complained that the area "stinks" and you can't turn a corner without tripping over heaps of waste.Huge rats plaguing rubbish-riddled Birmingham amidst the bin worker's strike are terrifying locals as the industrial action, which started early this year, continues.The clash between waste collector's union Unite and Birmingham City Council over the scrapping of a "safety-critical role" and pay cuts has led to indefinite strikes.Overflowing bins have caused utter carnage, with chaos set to "worsen", taxi drivers are warning.As residents, workers and shoppers desperately try to avoid the vermin-hit streets, cabbie Abid Hussain said: "The garbage is piling up, the vermin are coming out. It is disgusting!"The city is filthy, it stinks. It is a health issue and the situation will only get worse."The driver of 32 years slammed authorities for allowing Britain’s second biggest city to "go to the rats."Abid, speaking exclusively to The Sun, sighed: "It should never have come to this. People are terrified to come out."No one wants to see rats scurrying around all the un-emptied bins and the rubbish dumped in streets, alleyways and gardens."It is a terrible advert for the city where I have worked for more than three decades. I am a barometer for Birmingham and this is the worst it gets."
"I want to thank residents for their continued patience under difficult circumstances and the community groups who have been working hard within their communities to help with clear-up.

"I would reiterate that we have made a fair and reasonable offer to our workers which means none of them have to lose any money and I would urge Unite to reconsider their position."

Unite said the major incident declaration was an "attempt to crush any opposition to attacks on jobs, pay and conditions".

General secretary Sharon Graham said: "Birmingham council could easily resolve this dispute but instead it seems hellbent on imposing its plan of demotions and pay cuts at all costs.

"If that involves spending far more than it would cost to resolve the strike fairly, they don't seem to care.

"We can only conclude that this massive pay cut for hundreds of refuse workers is only the start and this is really about stamping out any future opposition to its plans to unleash austerity 2.0 on Birmingham.

"I urge Birmingham council to rethink this disastrous strategy and to find a way forward that doesn't involve workers and communities having to pay for politicians' mistakes.

Read More on The Sun

RIVER TRAGEDY Girl, 11, missing after falling into River Thames while playing is named

bikini babe Amanda Holden, 54, shows off age-defying body in a barely there silver bikini
"Unite will never accept attacks on our members and we will continue to defend Birmingham's refuse workforce to the hilt."

Birmingham City Council did not wish to comment further when approached by The Sun.''',
        openai_api_key=os.getenv('API_KEY')
    )
    locations = parser.parse()
    print(json.dumps(locations, indent=2, ensure_ascii=False))
