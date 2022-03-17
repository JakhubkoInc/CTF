import json
from datetime import datetime
from typing import Union

from ..lib import auxiliary
from colour import Color
from ..conf.projectdir import *
from ..lib.templating.pytest import TaskTemplate


class JSGen:
    
    @staticmethod
    def _js_repr(value):
        if isinstance(value,Union[int,float]):
            return str(value)
        elif isinstance(value,str):
            return repr(value)
        else:
            try:
                return json.dumps(value)
            except:
                return f'"{str(value)}"'

    @staticmethod
    def declare_vars(**kwargs):
        pairs = [f"{key} = {JSGen._js_repr(kwargs[key])};" for key in kwargs]
        return Scripts.AS_JS.format(js="\n".join(pairs))
    

class MDGen:

    @staticmethod
    def color_wrap(markdown:str, color:Union[str,Color], style="", end="  \n"):
        """Wraps markdown into a <span>, sets color (&style).

        Args:
            markdown ([type]): own markdown
            color ([type]): span color style
            style (str, optional): optional extra style. Defaults to "".
            end (str, optional): end of line. Defaults to "\s\s\\n".

        Returns:
            (str): adjusted markdown
        """
        return f'<span style="color:{color};{style}">{markdown}</span>{end}'

    @staticmethod
    def style_wrap(markdown:str, style="", end="  \n"):
        """Wraps markword into a <div>, optionally sets css style.

        Args:
            markdown (str): own markdown
            style (str, optional): optional style. Defaults to "".
            end (str, optional): end of line. Defaults to "  \n".

        Returns:
            (str): adjusted markdown
        """
        return f'<div style="{style}">{markdown}</div>{end}'
    
    @staticmethod
    def banner_block(markdown:str) -> str:
        """adds '> ' prefix to a markdown

        Args:
            markdown (str): own markdown

        Returns:
            str: adjusted markdown
        """
        return f"> {markdown}  \n"

class MDBanners: 
    """
    Pre-generated commonly used markup blocks (banners)
    """
    
    # tags
    NO_TEST_DATA = MDGen.banner_block(
                        MDGen.color_wrap(
                            Extras.NO_TEST_DATA,
                            Colors.ORANGE,
                            Style.FONT_BOLD,
                            end=''
                        )
                    )
    
    TESTS_OK = MDGen.banner_block(
                        MDGen.color_wrap(
                            Extras.TESTS_OK,
                            Colors.NICE_GREEN,
                            Style.FONT_BOLD,
                            end=''
                        )
                    )
    
    TESTS_SKIPPED = MDGen.banner_block(
                        MDGen.color_wrap(
                            Extras.TESTS_SKIP,
                            Colors.YELLOW,
                            Style.FONT_BOLD,
                            end=''
                        )
                    ) 
  

def update_task_md(md_path, task_template:TaskTemplate, task_dir_path):
    
    now = datetime.now()
    deadline_date = datetime.strptime(task_template.deadline(), DATETIME_FORMAT)
    
    colours = list(Colors.NICE_RED.range_to(Colors.NICE_GREEN,11))
    # up to 200% if got more than max points
    colours.extend(Color("#44d4db").range_to(Color("#dd2cdf"),10)) 

    got_points,max_points = task_template.points()
    perc = round((got_points/max_points)*100,2)
    perc_color = colours[round(perc/10)]
    
    have_test_data = True
    
    # do we have some testing data?
    if len(auxiliary.flatten(task_template.testing_sets().values())) == 0:
        task_template.markdown().header().append(MDBanners.NO_TEST_DATA)
        have_test_data = False
    else:
        task_template.markdown().header().extend([
            MDGen.banner_block(
                Extras.FOUND_TESTING_SETS.format(
                    setsLen=len(task_template.testing_sets()),
                    sets=", ".join([f"{item}({len(task_template.testing_sets()[item])})" for item in task_template.testing_sets()])
                )
            ),
            Extras.NL
        ])
    
    # if passed.lock exists and no testing data found -> tests were skipped otherwise tests passed    
    if (task_dir_path / Files.PASSED_LOCK_FILE_NAME).exists():
        if have_test_data:
            task_template.markdown().header().append(MDBanners.TESTS_OK)
        else:
            task_template.markdown().header().append(MDBanners.TESTS_SKIPPED)

    # append last update datetime    
    task_template.markdown.header.extend([
        Extras.NL,
        MDGen.banner_block(
            Extras.DEADLINE_TIMEOUT_PLACEHOLDER
        ),
        Extras.NL,
        MDGen.banner_block(
            Extras.SHOW_TEMPLATE_BUTTON  
        ),
        Extras.LINE,
        Extras.LAST_UPDATE.format(lastUpdateDate=now)
    ])

    # footer: copyright :D
    task_template.markdown().footer().append(
        MDGen.style_wrap(
            Extras.RIGHTS.format(year=datetime.now().year),
            Style.ALING_RIGHT
        )
    )

    # create markdown payload data and create the file
    deadline_color = Colors.NICE_GREEN if now < deadline_date else Colors.NICE_RED
    format_payload = {}
    export_vars = JSGen.declare_vars(deadlineDate=deadline_date)
    
    format_payload.update(task_template)
    format_payload.update({
        "points": MDGen.color_wrap(got_points, perc_color,end=""),
        "percentPoints": MDGen.color_wrap(perc, perc_color,end=""),
        "deadline": MDGen.color_wrap(deadline_date,deadline_color,end=""),
        "headerExtra": "".join(task_template.markdown().header()),
        "footer": "".join(task_template.markdown().footer()),
        "deadlineDate": deadline_date,
        "gotPoints": task_template.points()[0],
        "maxPoints": task_template.points()[1],
        "scripts": "".join([
            export_vars,
            Scripts.DEADLINE_TIMEOUT.format(deadlineDate=deadline_date),
            Scripts.FONTAWESOME
        ])
    })
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(Files.DEFAULT_MD.format(**format_payload))
