from IPython.display import display
import ipywidgets as widgets
from simpleac import SimPleAC
#from tutorial import Tutorial
from monte_carlo import monte_carlo_results
import time
import plotly.graph_objects as go
import pickle
import os
import csv

TUTORIAL = "tutorial"
CONTROL = "control"
MARGIN = "margin"
ROBUST_PERFORMANCE = "robust_performance"
ROBUST_GAMMA = "robust_gamma"

'''
subs - function that generates substitutions based on the lever widgets
model_gen - function that generates model
'''
def setup(levers, subs, model_gen, condition, exp=True):
    if exp:
        subj = widgets.Text(description='Subject-ID')
        path = "data/%s/%.0f/" % (condition, time.time())
        os.makedirs(path)

    button = widgets.Button(description="Run Simulation")

    levers_text = []
    for lever in levers:
        lever.style = {'description_width': '200px'}
        lever.layout.width = '800px'
        lever.continuous_update = True
        lever.readout = False
        lever_text = widgets.FloatText(
            disabled=False,
            continuous_update=True,
            margin = '0 80px 50px 0'
        )
        widgets.link((lever, 'value'), (lever_text, 'value'))
        levers_text.append(lever)
        levers_text.append(lever_text)

    progress = widgets.FloatProgress(value=0.0,
                                     min=0.0,
                                     max=1.0, 
                                     description='Loading:',
                                     bar_style='info',
                                     orientation='horizontal')
    progress.layout.visibility = 'hidden'

    out = widgets.Output(layout={'height': '50px',
                                 'border': 'none'})
    ifeas = widgets.Output(layout={'height': '150px',
                                   'border': 'none'})
    with ifeas:
        print("List of Infeasible Conditions:")

    fig = go.FigureWidget()
    fig.update_layout(
        autosize=False,
        width=800,
        height=600,
        yaxis=go.layout.YAxis(
            title_text="Failure Rate",
            range=[0,100],
            tickmode = 'array',
            tickvals = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100],
            ticktext = ["0%", "10%", "20%", "30%", "40%", "50%", "60%", "70%", "80%", "90%", "100%"]
        ),
        xaxis=go.layout.XAxis(
            title_text="Fuel Consumed (lbs)",
            range=[900,2000]
        )
    )
    fig.add_shape(
        go.layout.Shape(
            type="rect",
            x0=1200,
            y0=0,
            x1=2000,
            y1=10,
            fillcolor="rgba(240,255,220,0.4)",
            line=dict(
                color="white",
                width=1,
            ),
    ))
    fig.add_shape(
        go.layout.Shape(
            type="rect",
            x0=900,
            y0=30,
            x1=1100,
            y1=100,
            fillcolor="rgba(220,255,240,0.4)",
            line=dict(
                color="white",
                width=1,
            ),
    ))
    fig.add_shape(
        go.layout.Shape(
            type="rect",
            x0=900,
            y0=0,
            x1=1200,
            y1=30,
            fillcolor="rgba(200,255,200,0.4)",
            line=dict(
                color="white",
                width=1,
            ),
    ))
    fig.update_shapes(dict(xref='x', yref='y'))
    fig.add_trace(
        go.Scatter(mode = 'lines+markers'))
    diagram = go.FigureWidget();
    diagram.add_scatter(line={"color": "black"});
    diagram.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        autosize=False,
        width=800,
        height=800,
        yaxis=go.layout.YAxis(
            showgrid=False,
            showticklabels=False,
            range=[-5,25]
        ),
        xaxis=go.layout.XAxis(
            showgrid=False,
            showticklabels=False,
            range=[-15,15]
        )
    );
    diagram.data[0].mode = 'lines';

    item_layout = widgets.Layout(margin='50px',
                                 justify_content='space-around',
                                 justify_items='center',
                                 align_content='space-evenly',
                                 align_items='center')
    
    def draw_diagram(wing_length=16, wing_area=23, fuselage_volume=0.6):
        plane_length = 20
        tail_length = plane_length*.1
        tail_taper = tail_length*.5
        wing_taper = plane_length*.6
        wing_start = wing_taper - .6*wing_area/(wing_length/2)
        wing_end = wing_start + wing_area/(wing_length/2)
        nose_length = plane_length*.96

        fuselage_width = ((fuselage_volume*25+5)/plane_length)**.5
        tail_width = fuselage_width + wing_length/8
        wing_width = wing_length/2

        x = [
            tail_width, #0
            tail_width, #1
            fuselage_width, #2
            fuselage_width, #3
            wing_width, #4
            wing_width, #5
            fuselage_width, #6
            fuselage_width, #7
            0, #8
        ]

        x = x + [-1*i for i in x[7::-1]] + [tail_width]
        
        y = [
            0, #0
            tail_taper, #1
            tail_length, #2
            wing_start, #3
            wing_start, #4
            wing_taper, #5
            wing_end, #6
            nose_length, #7
            plane_length, #8
        ]
        y = y + y[7::-1] + [0]
        return x, y

    diagram.data[0].x, diagram.data[0].y = draw_diagram()
    
    x = []
    y = []
    conds = []
    iconds = []
    times = []
    start_time = time.time()#dt.now()

    def on_button_clicked(b):
        m = model_gen()
        m.substitutions.update(subs(levers))
        cond = str([lever.value for lever in levers])
        out.clear_output()
        
        if cond in iconds:
            with out:
                print(cond + " already tested")
                print("Infeasible conditions")
        
        elif cond in conds:
            with out:
                print(cond + " already tested")
                i = conds.index(cond)
                print("Fuel consumption: %i lbs" % x[i])
                print("    Failure rate: % 2.1f%% " % y[i])
        
        else:
            with out:
                print(cond)

            try:
                if condition in [CONTROL, MARGIN]:
                    sol = m.localsolve(verbosity = 0)
                    if exp:
                        filename = path + "%.0f" % (time.time()-start_time)
                        sol.save(filename)
                    sol_wing_area = sol("S").magnitude
                    sol_wing_length = ((sol("A").magnitude)*float(sol_wing_area))**.5
                    sol_fuel = sol("V_f_fuse").magnitude
                    diagram.data[0].x, diagram.data[0].y = draw_diagram(sol_wing_length, 
                                                                        sol_wing_area, 
                                                                        sol_fuel)
                elif condition == TUTORIAL:
                    sol = m.solve(verbosity = 0)
                    if exp:
                        filename = path + "%.0f" % (time.time()-start_time)
                        sol.save(filename)
                    size = (sol("S_a").magnitude)/2
                    diagram.data[0].x, diagram.data[0].y = draw_diagram(16*size, 
                                                                        23*size, 
                                                                        0.6*size)
                else:
                    sol = m.robustsolve(verbosity=0)
                    m = SimPleAC()
                    if exp:
                        filename = path + "%.0f" % (time.time()-start_time)
                        sol.save(filename)
                    sol_wing_area = sol("S").magnitude
                    sol_wing_length = ((sol("A").magnitude)*float(sol_wing_area))**.5
                    sol_fuel = sol("V_f_fuse").magnitude
                    diagram.data[0].x, diagram.data[0].y = draw_diagram(sol_wing_length, 
                                                                        sol_wing_area, 
                                                                        sol_fuel)
            except Exception as e:
                with out:
                    print("Infeasible Conditions")
                with ifeas:
                    print(cond)
                iconds.append(cond)
                filename = path + "%.0f" % (time.time()-start_time) + ".txt"
                f = open(filename, "w+")
                f.write()
                f.close()
                return

            
            if condition == TUTORIAL:
                performance = sol("C_o").magnitude
                failure = sol("F_a").magnitude
                with out:
                        print("Fuel consumption: %i lbs" % performance)
                        print("    Failure rate: % 2.1f%% " % failure)
            else:
                progress.value = 0
                progress.layout.visibility = None
                performance, failure = monte_carlo_results(m, progress, out, sol=sol)

            if performance:
                x.append(performance)
                y.append(failure)
                conds.append(cond)
                times.append(time.time()-start_time)
                fig.data[0].x = x
                fig.data[0].y = y
                fig.data[0].hovertext = conds
                import numpy as np
                fig.data[0].marker=dict(
                    size=[7]*(len(times) - 2) + [12, 18][:len(times)],
                    showscale=False,
                    color=["#aa44ff"]*(len(times) - 2) + ["#dd44cc", "#ff44aa"][:len(times)],
                )
                fig.data[0].line={
                    "color":'rgba(170, 68, 255, 0.2)'
                }
        progress.layout.visibility = 'hidden'
    button.on_click(on_button_clicked)

    col1 = widgets.VBox(levers_text + [button, fig, progress, out])
    
    left = widgets.VBox(levers_text + [widgets.HBox([button, progress]), out, fig])
    right = widgets.VBox([ifeas, diagram])
    
    return widgets.HBox([left, right], layout=item_layout)
