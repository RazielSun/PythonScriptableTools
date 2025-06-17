import unreal


def create_delegate(delegate_class, function):
    delegate = delegate_class()
    delegate.bind_callable(function)
    return delegate


@unreal.uclass()
class PythonSimpleToolPropertySet(unreal.EditorScriptableInteractiveToolPropertySet):
    bTestProperty = unreal.uproperty(bool, meta=dict(Category="Test"))

    def _post_init(self) -> None:
        unreal.log("PythonSimpleToolPropertySet _post_init")


@unreal.uclass()
class PythonSimpleToolActor(unreal.StaticMeshActor):

    def _post_init(self) -> None:
        static_mesh = unreal.EditorAssetLibrary.load_asset(
            "/Engine/BasicShapes/Cube.Cube"
        )
        self.static_mesh_component.set_static_mesh(static_mesh)
        unreal.log("PythonSimpleToolActor _post_init")


@unreal.uclass()
class PythonSimpleTool(unreal.EditorScriptableModularBehaviorTool):
    tool_property_set = None
    mouse_pos = unreal.Vector(0, 0, 0)
    actor_instance: unreal.StaticMeshActor = None
    tool_set_key = unreal.uproperty(str, meta=dict(Category="Settings"))
    point_set = None

    def _post_init(self) -> None:
        unreal.log("PythonSimpleTool _post_init")
        self.set_editor_property("tool_name", "Simple")
        self.set_editor_property("tool_long_name", "Simple Long Name")
        self.set_editor_property("tool_category", "Examples")
        self.set_editor_property("custom_icon_path", "Icons/Tool_SimpleIcon_40px.png")
        self.set_editor_property("tool_set_key", "PythonSimpleToolConfig")

    @unreal.ufunction(override=True)
    def on_script_setup(self):
        unreal.log(f"on_script_setup")

        self.add_single_click_behavior(
            create_delegate(unreal.TestIfHitByClickDelegate, self.on_begin_if_click),
            create_delegate(unreal.OnHitByClickDelegate, self.on_hit_by_click),
            unreal.MouseBehaviorModiferCheckDelegate(),
            capture_priority=100,
            mouse_button=unreal.ScriptableToolMouseButton.LEFT_BUTTON,
            hit_test_on_release=True,
        )

        self.add_mouse_hover_behavior(
            create_delegate(
                unreal.BeginHoverSequenceHitTestDelegate, self.on_begin_if_hover
            ),
            unreal.OnBeginHoverDelegate(),
            create_delegate(unreal.OnUpdateHoverDelegate, self.on_update_hover),
            unreal.OnEndHoverDelegate(),
            unreal.MouseBehaviorModiferCheckDelegate(),
            capture_priority=100,
        )

        self.tool_property_set, out_pin = self.add_property_set_of_type(
            PythonSimpleToolPropertySet, identifier="Settings"
        )
        unreal.log(f"on_script_setup: tool_property_set {self.tool_property_set}")
        self.restore_property_set_settings(
            self.tool_property_set, self.get_editor_property("tool_set_key")
        )

        actor_instance = unreal.PythonScript_Utils.spawn_transient_editor_actor(
            self, PythonSimpleToolActor, unreal.Transform()
        )
        # self.set_editor_property('actor_instance', actor_instance)
        self.actor_instance = actor_instance

        point_set = self.add_point_set()
        self.point_set = point_set

    @unreal.ufunction(override=True)
    def on_script_shutdown(self, shutdown_type):
        unreal.log(f"on_script_shutdown {shutdown_type}")
        self.save_property_set_settings(
            self.tool_property_set, self.get_editor_property("tool_set_key")
        )
        self.tool_property_set = None
        if self.actor_instance:
            self.actor_instance.destroy_actor()

    @unreal.ufunction(override=True)
    def on_script_tick(self, delta_time: float):
        pass
        # unreal.log(f"local func tick {delta_time}")

    @unreal.ufunction(override=True)
    def on_script_render(self, render_api):
        render_api.draw_line(
            start=unreal.Vector(0, 0, 0),
            end=unreal.Vector(500, 500, 50),
            color=unreal.LinearColor(1, 0, 0, 1),
            thickness=15.0,
        )

    def line_trace(self, world_ray):
        start_vector, end_vector = unreal.GeometryScript_Ray.get_ray_start_end(
            world_ray
        )
        actors_to_ignore = []
        if self.actor_instance:
            actors_to_ignore.append(self.actor_instance)
        out_hit = unreal.SystemLibrary.line_trace_single(
            self,
            start_vector,
            end_vector,
            unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,
            False,  # bTraceComplex
            actors_to_ignore,
            unreal.DrawDebugTrace.NONE,
            False,  # bIgnoreSelf
            unreal.LinearColor(1, 0, 0, 1),  # Trace color
            unreal.LinearColor(1, 1, 1, 1),  # Trace hit color
            1.0,  # Draw time
        )
        return out_hit

    def on_begin_if_hover(self, current_pos, modifiers):
        out_hit = self.line_trace(current_pos.world_ray)
        depth = unreal.PythonScript_Utils.get_hit_depth_from_hit_result(out_hit)
        return unreal.ScriptableTools_Util.make_input_ray_hit(depth, None)
        # hit = unreal.InputRayHit()
        # hit.hit = True
        # return hit

    def on_update_hover(self, current_pos, modifiers):
        out_hit = self.line_trace(current_pos.world_ray)
        hit_pos = unreal.PythonScript_Utils.get_location_from_hit_result(out_hit)
        self.mouse_pos = hit_pos
        if self.actor_instance:
            self.actor_instance.set_actor_location(self.mouse_pos, False, True)
        # unreal.log(f"on_update_hover from {start_vector} to {end_vector} -> {self.mouse_pos}")

    def on_begin_if_click(self, current_pos, mouse_button):
        out_hit = self.line_trace(current_pos.world_ray)
        depth = unreal.PythonScript_Utils.get_hit_depth_from_hit_result(out_hit)
        return unreal.ScriptableTools_Util.make_input_ray_hit(depth, None)

    def on_hit_by_click(self, current_pos, modifiers, mouse_button):
        out_hit = self.line_trace(current_pos.world_ray)
        hit_pos = unreal.PythonScript_Utils.get_location_from_hit_result(out_hit)
        if self.point_set:
            point = self.point_set.add_point()
            point.set_point_position(hit_pos)
            point.set_point_color(unreal.LinearColor(1, 0, 0, 1).to_color(True))
            point.set_point_size(50.0)
