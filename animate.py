from manim import *
import numpy as np
import argparse
import json
import os

class PathAnimation(Scene):

    def __init__(self,model_name,temperature,rounds_per_temp,renderer = None, camera_class = None, always_update_mobjects = False,random_seed=None,skip_animations=False):
        super().__init__(renderer, camera_class, always_update_mobjects, random_seed, skip_animations)
        self.model_name = model_name
        self.temperature = round(float(temperature),1)
        self.rounds_per_temp = int(rounds_per_temp)

    def construct(self):

        file_name = self.model_name.split(':')[0] + "_" + self.model_name.split(':')[1]
        temperature = self.temperature
        data_file = os.path.join('data',f"{file_name}.json")

        step_number = 1

        with open(data_file,'r') as f:
            data = json.load(f)

        paths = []
        for curr_round in range(self.rounds_per_temp):
            paths.append(data[self.model_name][f"TEMP_{temperature}"][f"R_{curr_round}"][1])

        colors = [PURE_RED,PURE_BLUE,PURE_GREEN,YELLOW,PINK] 

        title = Text(f"Model: {self.model_name}\nTemperature: {temperature}", font="Cascadia Mono",font_size=20, color=WHITE).to_corner(UL)
        step_text = Text(f"Step {step_number}",font_size=18,color=WHITE,font="Cascadia Mono").to_corner(DL)

        grid = NumberPlane(
            x_range=[-20, 20, 1],
            y_range=[-20, 20, 1],
            x_length=20,
            y_length=20,
            background_line_style={
                "stroke_color": WHITE,
                "stroke_opacity": 0.3
            },
            axis_config = {
                "stroke_width": 2,
                "font_size": 18,
                "color": WHITE,
            }
        ).add_coordinates()
        
        self.play(Create(grid))
        self.play(Write(title))
        self.wait(0.2)
        self.add_legend(colors,self.rounds_per_temp)
        self.play(Write(step_text))
        self.wait(0.2)

        dots,lines = [], []

        for i,path in enumerate(paths):
            # print(f"{i} --- {path}")
            points = [np.array([x*0.5,y*0.5,0]) for x,y in path]
            dot = Dot(points[0],color=colors[i%len(colors)]).scale(1)
            line = VMobject(color=colors[i%len(colors)])
            line.set_points_as_corners([points[0],points[0]])
            line.set_stroke(width=3+i*0.5,opacity=0.7)
            dots.append(dot)
            lines.append(line)
            self.add(dot,line)
        
        for step in range(len(paths[0])-1):
            animations = []
            for i,path in enumerate(paths):
                points = [np.array([x*0.5,y*0.5,0]) for x,y in path]
                if step < len(points) - 1:
                    animations.extend([
                        dots[i].animate.move_to(points[step+1]),
                        Create(Line(points[step],points[step+1],color=colors[i%len(colors)],stroke_width=3+i*0.5,stroke_opacity=0.7))
                    ])
            
            step_number+=1
            next_step_text = Text(f"Step {step_number}",font_size=18,color=WHITE,font="Cascadia Mono").to_corner(DL)
            animations.append(ReplacementTransform(step_text,next_step_text))
            step_text = next_step_text

            if animations:
                self.play(*animations,run_time=0.8)
                self.wait(0.1)

        self.wait(4)
    

    def add_legend(self, colors, num_rounds):
        legend_items = []

        for i in range(num_rounds):
            color = colors[i % len(colors)]
            square = Square(side_length=0.3, fill_color=color, fill_opacity=1).set_stroke(width=0)
            label = Text(f"Round {i+1}", font_size=15, color=WHITE,font="Cascadia Mono").next_to(square, RIGHT, buff=0.2)
            item = VGroup(square, label)
            legend_items.append(item)

        legend = VGroup(*legend_items).arrange(DOWN, aligned_edge=LEFT, buff=0.1)

        box = SurroundingRectangle(legend, color=WHITE, buff=0.3)

        legend_with_box = VGroup(box, legend).to_corner(UR)

        self.play(FadeIn(legend_with_box))
        self.wait(1)


if __name__ == "__main__":
        parser = argparse.ArgumentParser()
        parser.add_argument('--model_name','-m',type=str,required=True)
        parser.add_argument('--temperature','-t',type=str,required=True)
        parser.add_argument('--rounds_per_temp','-r',type=str,required=True)
        parser.add_argument('--quality', '-q', 
                       choices=['l', 'm', 'h', 'p', 'k'], 
                       default='l',)
        args = parser.parse_args()
        quality_map = {
                    'e': 'example_quality',
                    'l': 'low_quality',
                    'm': 'medium_quality',
                    'h': 'high_quality',
                    'p': 'production_quality',
                    'k': 'fourk_quality'
        }
        config.quality = quality_map[args.quality]
        config.save_last_frame = True
        # config.images_dir = "./media/images"
        # config.output_file = f"{args.model_name}_temp-{args.temperature}"

        scene = PathAnimation(args.model_name,args.temperature,args.rounds_per_temp)
        scene.render()