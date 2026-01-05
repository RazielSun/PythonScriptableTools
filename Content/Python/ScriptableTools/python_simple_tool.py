import unreal as ue
from .utils import create_delegate, break_hit_result


@ue.uclass()
class PythonSimpleToolPropertySet(ue.EditorScriptableInteractiveToolPropertySet):
    bTestProperty = ue.uproperty(bool, meta=dict(Category="Test"))

    def _post_init(self) -> None:
        ue.log("PythonSimpleToolPropertySet _post_init")


@ue.uclass()
class PythonSimpleToolActor(ue.StaticMeshActor):

    def _post_init(self) -> None:
        static_mesh = ue.EditorAssetLibrary.load_asset(
            "/Engine/BasicShapes/Cube.Cube"
        )
        self.static_mesh_component.set_static_mesh(static_mesh)
        ue.log("PythonSimpleToolActor _post_init")


@ue.uclass()
class PythonSimpleTool(ue.EditorScriptableModularBehaviorTool):
    tool_property_set = None
    mouse_pos = ue.Vector(0, 0, 0)
    actor_instance: ue.StaticMeshActor = None
    tool_set_key = ue.uproperty(str, meta=dict(Category="Settings"))
    point_set = None

    def _post_init(self) -> None:
        ue.log("PythonSimpleTool _post_init")
        self.set_editor_property("show_tool_in_editor", False) # Comment this line to show a tool in editor
        self.set_editor_property("tool_name", "Simple")
        self.set_editor_property("tool_long_name", "Simple Long Name")
        self.set_editor_property("tool_category", "Examples")
        self.set_editor_property("custom_icon_path", "Icons/Tool_SimpleIcon_40px.png")
        self.set_editor_property("tool_set_key", "PythonSimpleToolConfig")

    @ue.ufunction(override=True)
    def on_script_setup(self):
        ue.log(f"on_script_setup")

        self.add_single_click_behavior(
            create_delegate(ue.TestIfHitByClickDelegate, self.on_begin_if_click),
            create_delegate(ue.OnHitByClickDelegate, self.on_hit_by_click),
            ue.MouseBehaviorModiferCheckDelegate(),
            capture_priority=100,
            mouse_button=ue.ScriptableToolMouseButton.LEFT_BUTTON,
            hit_test_on_release=True,
        )

        self.add_mouse_hover_behavior(
            create_delegate(
                ue.BeginHoverSequenceHitTestDelegate, self.on_begin_if_hover
            ),
            ue.OnBeginHoverDelegate(),
            create_delegate(ue.OnUpdateHoverDelegate, self.on_update_hover),
            ue.OnEndHoverDelegate(),
            ue.MouseBehaviorModiferCheckDelegate(),
            capture_priority=100,
        )

        self.tool_property_set, out_pin = self.add_property_set_of_type(
            PythonSimpleToolPropertySet, identifier="Settings"
        )
        ue.log(f"on_script_setup: tool_property_set {self.tool_property_set}")
        self.restore_property_set_settings(
            self.tool_property_set, self.get_editor_property("tool_set_key")
        )

        actor_instance = ue.EditorLevelLibrary.spawn_actor_from_class(PythonSimpleToolActor, ue.Vector(0, 0, 0), ue.Rotator(0, 0, 0), True)
        self.actor_instance = PythonSimpleToolActor.cast(actor_instance)

        point_set = self.add_point_set()
        self.point_set = point_set

    @ue.ufunction(override=True)
    def on_script_shutdown(self, shutdown_type):
        ue.log(f"on_script_shutdown {shutdown_type}")
        self.save_property_set_settings(
            self.tool_property_set, self.get_editor_property("tool_set_key")
        )
        self.tool_property_set = None
        if self.actor_instance:
            self.actor_instance.destroy_actor()

    @ue.ufunction(override=True)
    def on_script_tick(self, delta_time: float):
        pass
        # unreal.log(f"local func tick {delta_time}")

    @ue.ufunction(override=True)
    def on_script_render(self, render_api):
        render_api.draw_line(
            start=ue.Vector(0, 0, 0),
            end=ue.Vector(500, 500, 50),
            color=ue.LinearColor(1, 0, 0, 1),
            thickness=15.0,
        )

    def line_trace(self, world_ray):
        start_vector, end_vector = ue.GeometryScript_Ray.get_ray_start_end(
            world_ray
        )
        actors_to_ignore = []
        if self.actor_instance:
            actors_to_ignore.append(self.actor_instance)
        out_hit = ue.SystemLibrary.line_trace_single(
            self,
            start_vector,
            end_vector,
            ue.TraceTypeQuery.TRACE_TYPE_QUERY1,
            False,  # bTraceComplex
            actors_to_ignore,
            ue.DrawDebugTrace.NONE,
            False,  # bIgnoreSelf
            ue.LinearColor(1, 0, 0, 1),  # Trace color
            ue.LinearColor(1, 1, 1, 1),  # Trace hit color
            1.0,  # Draw time
        )
        return out_hit

    def on_begin_if_hover(self, current_pos, modifiers):
        out_hit = self.line_trace(current_pos.world_ray)
        depth = break_hit_result(out_hit).get("distance")
        return ue.ScriptableTools_Util.make_input_ray_hit(depth, None)
        # hit = unreal.InputRayHit()
        # hit.hit = True
        # return hit

    def on_update_hover(self, current_pos, modifiers):
        out_hit = self.line_trace(current_pos.world_ray)
        hit_pos = break_hit_result(out_hit).get("location")
        self.mouse_pos = hit_pos
        if self.actor_instance:
            self.actor_instance.set_actor_location(self.mouse_pos, False, True)
        # unreal.log(f"on_update_hover from {start_vector} to {end_vector} -> {self.mouse_pos}")

    def on_begin_if_click(self, current_pos, mouse_button):
        out_hit = self.line_trace(current_pos.world_ray)
        depth = break_hit_result(out_hit).get("distance")
        return ue.ScriptableTools_Util.make_input_ray_hit(depth, None)

    def on_hit_by_click(self, current_pos, modifiers, mouse_button):
        out_hit = self.line_trace(current_pos.world_ray)
        hit_pos = break_hit_result(out_hit).get("location")
        if self.point_set:
            point = self.point_set.add_point()
            point.set_point_position(hit_pos)
            point.set_point_color(ue.LinearColor(1, 0, 0, 1).to_color(True))
            point.set_point_size(50.0)
