import unreal as ue
from .utils import create_delegate, break_hit_result


@ue.uclass()
class PyRoadToolPropertySet(ue.EditorScriptableInteractiveToolPropertySet):
    world_offset = ue.uproperty(ue.Vector, meta=dict(Category="Base"))
    force_snap = ue.uproperty(bool, meta=dict(Category="Snap"))
    snap_grid = ue.uproperty(ue.Vector2D, meta=dict(Category="Snap"))
    snap_offset = ue.uproperty(ue.Vector2D, meta=dict(Category="Snap"))
    lock_only_xy = ue.uproperty(bool, meta=dict(Category="Snap"))
    forced_z = ue.uproperty(bool, meta=dict(Category="Force Set"))
    forced_z_value = ue.uproperty(float, meta=dict(Category="Force Set"))
    show_grid = ue.uproperty(bool, meta=dict(Category="Visualize"))
    line_length = ue.uproperty(float, meta=dict(Category="Visualize"))

    def _post_init(self) -> None:
        self.set_editor_property("world_offset", ue.Vector(0,0,0))
        self.set_editor_property("force_snap", False)
        self.set_editor_property("snap_grid", ue.Vector2D(1200.0, 1200.0))
        self.set_editor_property("snap_offset", ue.Vector2D(0.0, 0.0))
        self.set_editor_property("lock_only_xy", False)
        self.set_editor_property("forced_z", False)
        self.set_editor_property("forced_z_value", 0.0)
        self.set_editor_property("show_grid", True)
        self.set_editor_property("line_length", 10000.0)
        ue.log("PyRoadToolPropertySet _post_init")


@ue.uclass()
class PyRoadToolActor(ue.StaticMeshActor):
    material_instance = None
    def _post_init(self) -> None:
        static_mesh = ue.EditorAssetLibrary.load_asset(
            "/Engine/BasicShapes/Cube.Cube"
        )
        self.static_mesh_component.set_static_mesh(static_mesh)
        self.static_mesh_component.set_collision_enabled(ue.CollisionEnabled.NO_COLLISION)
        self.static_mesh_component.set_editor_property("can_ever_affect_navigation", False)
        
        material = ue.EditorAssetLibrary.load_asset(
            "/PythonScriptableTools/Materials/MI_DebugDithered_Basic.MI_DebugDithered_Basic"
        )
        material_instance = ue.MaterialLibrary.create_dynamic_material_instance(self, material)
        material_instance.set_vector_parameter_value("Color", ue.LinearColor(1, 1, 0, 0.5))
        self.static_mesh_component.set_material(0, material_instance)
        ue.log("PyRoadToolActor _post_init")


@ue.uclass()
class PyRoadTool(ue.EditorScriptableModularBehaviorTool):
    tool_property_set = None
    ea_subsystem = None
    actor_location = ue.Vector(0, 0, 0)
    last_location = None
    actor_instance: ue.StaticMeshActor = None
    tool_set_key = ue.uproperty(str, meta=dict(Category="Settings"))
    point_set = None
    line_set = None
    current_line = None
    points = []

    def _post_init(self) -> None:
        self.set_editor_property("tool_name", "RoadTool")
        self.set_editor_property("tool_long_name", "Road Tool")
        self.set_editor_property("tool_category", "Build")
        self.set_editor_property("custom_icon_path", "Icons/Tool_SimpleIcon_40px.png")
        self.set_editor_property("tool_set_key", "PyRoadToolConfig")
        ue.log("PyRoadTool _post_init")

    @ue.ufunction(override=True)
    def on_script_setup(self):
        self.ea_subsystem = ue.get_editor_subsystem(ue.EditorActorSubsystem)
        
        self.add_multi_click_sequence_behavior(
            create_delegate(ue.OnBeginSequencePreviewDelegate, self.on_begin_preview_seq),
            create_delegate(ue.CanBeginClickSequenceDelegate, self.can_begin_click_seq),
            create_delegate(ue.OnBeginClickSequenceDelegate, self.on_begin_click_seq),
            create_delegate(ue.OnNextSequencePreviewDelegate, self.on_next_preview_seq),
            create_delegate(ue.OnNextSequenceClickDelegate, self.on_next_click_seq),
            create_delegate(ue.OnTerminateClickSequenceDelegate, self.on_terminate_click_seq),
            ue.RequestAbortClickSequenceDelegate(),
            ue.MouseBehaviorModiferCheckDelegate(),
            ue.MouseBehaviorModiferCheckDelegate(),
            capture_priority=100,
            mouse_button=ue.ScriptableToolMouseButton.LEFT_BUTTON
        )

        self.tool_property_set, out_pin = self.add_property_set_of_type(
            PyRoadToolPropertySet, identifier="Settings"
        )
        self.restore_property_set_settings(
            self.tool_property_set, self.get_editor_property("tool_set_key")
        )

        actor_instance = self.ea_subsystem.spawn_actor_from_class(PyRoadToolActor, ue.Vector(0, 0, 0), ue.Rotator(0, 0, 0), True)
        self.actor_instance = actor_instance

        point_set = self.add_point_set()
        self.point_set = point_set
        
        line_set = self.add_line_set()
        self.line_set = line_set

    @ue.ufunction(override=True)
    def on_script_shutdown(self, shutdown_type):
        self.last_location = None
        if shutdown_type == ue.ToolShutdownType.COMPLETED:
            actor = self.create_new_spline()
            if actor:
                self.ea_subsystem.set_selected_level_actors([actor])
            ue.log("Tool Completed")
        self.save_property_set_settings(
            self.tool_property_set, self.get_editor_property("tool_set_key")
        )
        self.tool_property_set = None
        if self.actor_instance:
            self.actor_instance.destroy_actor()

    @ue.ufunction(override=True)
    def on_script_tick(self, delta_time: float):
        pass

    @ue.ufunction(override=True)
    def on_script_render(self, render_api):
        if self.tool_property_set:
            if self.tool_property_set.show_grid:
                color = ue.LinearColor(0, 0.2, 1, 0.7)
                thickness = 2.0
                h_start = self.actor_location + ue.Vector(1, 0, 0) * self.tool_property_set.line_length
                h_end = self.actor_location + ue.Vector(-1, 0, 0) * self.tool_property_set.line_length
                v_start = self.actor_location + ue.Vector(0, 1, 0) * self.tool_property_set.line_length
                v_end = self.actor_location + ue.Vector(0, -1, 0) * self.tool_property_set.line_length
                # draw horizontal line
                render_api.draw_line(
                    start=h_start,
                    end=h_end,
                    color=color,
                    thickness=thickness,
                )
                # draw vertical line
                render_api.draw_line(
                    start=v_start,
                    end=v_end,
                    color=color,
                    thickness=thickness,
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
        if out_hit is None:
            out_hit = ue.HitResult()
        # ue.log(f"line_trace: {start_vector} to {end_vector} hit {out_hit}")
        return out_hit
    
    def update_actor_location(self, location : ue.Vector, snap : bool = False):
        actor_location = location + self.tool_property_set.world_offset
        if snap or self.tool_property_set.force_snap:
            snap_x = self.tool_property_set.snap_grid.x
            snap_y = self.tool_property_set.snap_grid.y
            offset_x = self.tool_property_set.snap_offset.x
            offset_y = self.tool_property_set.snap_offset.y
            actor_location.x = round(actor_location.x / snap_x) * snap_x + offset_x
            actor_location.y = round(actor_location.y / snap_y) * snap_y + offset_y
        if self.tool_property_set.forced_z:
            actor_location.z = self.tool_property_set.forced_z_value
        if self.last_location is not None:
            if self.tool_property_set.lock_only_xy:
                delta = self.last_location - actor_location
                if abs(delta.x) > abs(delta.y):
                    actor_location.y = self.last_location.y
                else:
                    actor_location.x = self.last_location.x
        self.actor_location = actor_location
        if self.actor_instance:
            self.actor_instance.set_actor_location(self.actor_location, False, True)
    
    def update_active_click_pos(self, click_pos, snap=False):
        out_hit = self.line_trace(click_pos.world_ray)
        hit_pos = break_hit_result(out_hit).get("location")
        self.update_actor_location(hit_pos, snap)
    
    def create_new_line(self):
        if self.line_set:
            new_line = self.line_set.add_line()
            new_line.set_line_start(self.actor_location)
            new_line.set_line_end(self.actor_location)
            new_line.set_line_color(ue.LinearColor(1, 1, 0, 1).to_color(True))
            new_line.set_line_thickness(10.0)
            new_line.set_line_depth_bias(10.0)
            return new_line
        return None
    
    def create_new_point(self, start_point = False, point_size = 20.0):
        if self.point_set:
            new_point = self.point_set.add_point()
            new_point.set_point_position(self.actor_location + ue.Vector(0, 0, point_size * 0.5))
            color = start_point and ue.LinearColor(1, 0, 0, 1) or ue.LinearColor(0, 0, 1, 1)
            new_point.set_point_color(color.to_color(True))
            new_point.set_point_size(point_size)
            new_point.set_point_depth_bias(10.0)
            self.points.append(self.actor_location)
            return new_point
        return None
    
    def create_zone_shape(self):
        if len(self.points) > 0:
            location = self.points[0]
            zone_shape = self.ea_subsystem.spawn_actor_from_class(ue.ZoneShape, location, ue.Rotator(0, 0, 0))
            component = zone_shape.shape_component
            zone_shape_points = []
            for (i, p) in enumerate(self.points):
                point = ue.ZoneShapePoint()
                point.position = p - location
                zone_shape_points.append(point)
            component.points = zone_shape_points
            return zone_shape
        return None
    
    def create_spline_actor(self):
        if len(self.points) > 0:
            location = self.points[0]
            spline_actor = self.ea_subsystem.spawn_actor_from_class(ue.STSplineActor, location, ue.Rotator(0, 0, 0))
            component = spline_actor.spline_component
            component.set_spline_points(self.points, ue.SplineCoordinateSpace.WORLD, False)
            for i in range(len(self.points)):
                component.set_spline_point_type(i, ue.SplinePointType.LINEAR, False)
            component.update_spline()
            spline_actor.set_editor_property("tags", ["road_spline"])
            return spline_actor
        return None
            
    def create_new_spline(self):
        spline_actor = self.create_spline_actor()
        if self.point_set:
            self.point_set.remove_all_points()
        if self.line_set:
            self.line_set.remove_all_lines()
        self.points.clear()
        return spline_actor

    def on_begin_preview_seq(self, click_pos, modifiers, mouse_button):
        self.update_active_click_pos(click_pos, modifiers.shift_down)
    
    def can_begin_click_seq(self, click_pos, mouse_button): # bool
        if mouse_button != ue.ScriptableToolMouseButton.LEFT_BUTTON:
            return False
        out_hit = self.line_trace(click_pos.world_ray)
        return break_hit_result(out_hit).get("blocking_hit")

    def on_begin_click_seq(self, click_pos, modifiers, mouse_button):
        self.update_active_click_pos(click_pos, modifiers.shift_down)
        self.create_new_point(True, 25.0)
        self.current_line = self.create_new_line()
        self.last_location = self.actor_location

    def on_next_preview_seq(self, click_pos, modifiers, mouse_button):
        self.update_active_click_pos(click_pos, modifiers.shift_down)
        if self.current_line:
            self.current_line.set_line_end(self.actor_location)
        
    def on_next_click_seq(self, click_pos, modifiers, mouse_button): # bool
        if modifiers.ctrl_down or mouse_button == ue.ScriptableToolMouseButton.RIGHT_BUTTON:
            # Request End Line
            self.create_new_spline()
            self.current_line = None
            self.last_location = None
            return False
        self.update_active_click_pos(click_pos, modifiers.shift_down)
        self.last_location = self.actor_location
        self.create_new_point()
        if self.current_line:
            self.current_line.set_line_end(self.actor_location)
            self.current_line.set_line_color(ue.LinearColor(0, 1, 0, 1).to_color(True))
            # Start a new line from the last point
            self.current_line = self.create_new_line()
        return True

    def on_terminate_click_seq(self, modifiers, mouse_button):
        # Request End Line
        pass
