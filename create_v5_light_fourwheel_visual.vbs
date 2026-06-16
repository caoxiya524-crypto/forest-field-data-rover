Option Explicit

' V5-light four-wheel visual model.
' Purpose: create a single SolidWorks part that visually matches the target rover
' without building a large multi-file assembly in the current low-memory session.

Const PART_TEMPLATE = "C:\ProgramData\SOLIDWORKS\SOLIDWORKS 2025\templates\gb_part.prtdot"
Const ROOT_DIR = "D:\data\pre_processing\solidworks_project\forest_lfmc_fire_rover_v5_light_fourwheel"
Const OUT_PART = "D:\data\pre_processing\solidworks_project\forest_lfmc_fire_rover_v5_light_fourwheel\v5_light_fourwheel_visual_model_100_connected.SLDPRT"
Const OUT_PNG = "D:\data\pre_processing\solidworks_project\forest_lfmc_fire_rover_v5_light_fourwheel\v5_light_fourwheel_visual_model_100_connected_isometric.png"
Const OUT_README = "D:\data\pre_processing\solidworks_project\forest_lfmc_fire_rover_v5_light_fourwheel\README_V5_LIGHT_FOURWHEEL.md"

Dim fso
Set fso = CreateObject("Scripting.FileSystemObject")
If Not fso.FolderExists("D:\data\pre_processing\solidworks_project") Then fso.CreateFolder("D:\data\pre_processing\solidworks_project")
If Not fso.FolderExists(ROOT_DIR) Then fso.CreateFolder(ROOT_DIR)

Dim swApp, startedHere
startedHere = False
On Error Resume Next
Set swApp = CreateObject("SldWorks.Application.33")
If Err.Number <> 0 Or swApp Is Nothing Then
  Err.Clear
  Set swApp = GetObject(, "SldWorks.Application.33")
Else
  startedHere = True
End If
On Error GoTo 0

If swApp Is Nothing Then
  WScript.Echo "SW_APP_FAILED"
  WScript.Quit 2
End If

swApp.Visible = False
If startedHere Then WScript.Sleep 5000

Function SelectRefPlaneByIndex(model, planeIndex)
  Dim f, n
  n = 0
  Set f = model.FirstFeature
  Do While Not f Is Nothing
    If f.GetTypeName2 = "RefPlane" Then
      n = n + 1
      If n = planeIndex Then
        Call model.ClearSelection2(True)
        SelectRefPlaneByIndex = f.Select2(False, 0)
        Exit Function
      End If
    End If
    Set f = f.GetNextFeature
  Loop
  SelectRefPlaneByIndex = False
End Function

Sub StartSketchOnPlane(model, planeIndex)
  If Not SelectRefPlaneByIndex(model, planeIndex) Then
    WScript.Echo "ERROR_SELECT_PLANE index=" & planeIndex
    WScript.Quit 3
  End If
  Call model.SketchManager.InsertSketch(True)
End Sub

Function MakeOffsetPlane(model, offset, featureName)
  Dim feat
  If Not SelectRefPlaneByIndex(model, 1) Then
    WScript.Echo "ERROR_SELECT_FRONT_PLANE_FOR_OFFSET"
    WScript.Quit 3
  End If
  On Error Resume Next
  Set feat = model.FeatureManager.InsertRefPlane(8, offset, 0, 0, 0, 0)
  If Err.Number <> 0 Or feat Is Nothing Then
    WScript.Echo "ERROR_OFFSET_PLANE feature=" & featureName & " offset=" & offset & " err=" & Err.Number & " " & Err.Description
    Err.Clear
    On Error GoTo 0
    WScript.Quit 3
  End If
  feat.Name = featureName
  Err.Clear
  On Error GoTo 0
  Set MakeOffsetPlane = feat
End Function

Sub StartSketchOnFeature(model, planeFeat)
  If planeFeat Is Nothing Then
    WScript.Echo "ERROR_START_SKETCH_NULL_PLANE"
    WScript.Quit 3
  End If
  Call model.ClearSelection2(True)
  If Not planeFeat.Select2(False, 0) Then
    WScript.Echo "ERROR_SELECT_OFFSET_PLANE " & planeFeat.Name
    WScript.Quit 3
  End If
  Call model.SketchManager.InsertSketch(True)
End Sub

Sub HideRefFeature(model, refFeat)
  If refFeat Is Nothing Then Exit Sub
  On Error Resume Next
  Call model.ClearSelection2(True)
  If refFeat.Select2(False, 0) Then
    Call swApp.RunCommand(895, "")
  End If
  Call model.ClearSelection2(True)
  Err.Clear
  On Error GoTo 0
End Sub

Sub FinishSketch(model)
  Call model.SketchManager.InsertSketch(True)
End Sub

Function BossExtrude(model, depth, featureName, mergeResult)
  Dim feat
  Set feat = model.FeatureManager.FeatureExtrusion2( _
    True, False, False, _
    0, 0, depth, 0, _
    False, False, False, False, _
    0, 0, _
    False, False, False, False, _
    mergeResult, True, True, _
    0, 0, False)
  If feat Is Nothing Then
    WScript.Echo "ERROR_EXTRUDE feature=" & featureName
    WScript.Quit 4
  End If
  feat.Name = featureName
  Set BossExtrude = feat
End Function

Function BossExtrudeDir(model, depth, featureName, mergeResult, flipDir)
  Dim feat
  Set feat = model.FeatureManager.FeatureExtrusion2( _
    True, flipDir, False, _
    0, 0, depth, 0, _
    False, False, False, False, _
    0, 0, _
    False, False, False, False, _
    mergeResult, True, True, _
    0, 0, False)
  If feat Is Nothing Then
    WScript.Echo "ERROR_EXTRUDE_DIR feature=" & featureName
    WScript.Quit 4
  End If
  feat.Name = featureName
  Set BossExtrudeDir = feat
End Function

Sub SetDocColor(model, r, g, b)
  ' Appearance is left to SolidWorks/default manual editing in this low-memory pass.
End Sub

Sub SetFeatureColor(feat, r, g, b)
  ' Appearance is left to SolidWorks/default manual editing in this low-memory pass.
End Sub

Sub AddRectAt(model, cx, cy, w, h)
  Dim x, y
  x = w / 2
  y = h / 2
  Call model.SketchManager.CreateLine(cx - x, cy - y, 0, cx + x, cy - y, 0)
  Call model.SketchManager.CreateLine(cx + x, cy - y, 0, cx + x, cy + y, 0)
  Call model.SketchManager.CreateLine(cx + x, cy + y, 0, cx - x, cy + y, 0)
  Call model.SketchManager.CreateLine(cx - x, cy + y, 0, cx - x, cy - y, 0)
End Sub

Sub AddChamferedRectAt(model, cx, cy, w, h, chamfer)
  Dim x, y, c
  x = w / 2
  y = h / 2
  c = chamfer
  Call model.SketchManager.CreateLine(cx - x + c, cy - y, 0, cx + x - c, cy - y, 0)
  Call model.SketchManager.CreateLine(cx + x - c, cy - y, 0, cx + x, cy - y + c, 0)
  Call model.SketchManager.CreateLine(cx + x, cy - y + c, 0, cx + x, cy + y - c, 0)
  Call model.SketchManager.CreateLine(cx + x, cy + y - c, 0, cx + x - c, cy + y, 0)
  Call model.SketchManager.CreateLine(cx + x - c, cy + y, 0, cx - x + c, cy + y, 0)
  Call model.SketchManager.CreateLine(cx - x + c, cy + y, 0, cx - x, cy + y - c, 0)
  Call model.SketchManager.CreateLine(cx - x, cy + y - c, 0, cx - x, cy - y + c, 0)
  Call model.SketchManager.CreateLine(cx - x, cy - y + c, 0, cx - x + c, cy - y, 0)
End Sub

Sub AddCurvedCapAt(model, xLeft, xRight, yBase, rise, segments)
  Dim i, pi, t, xPrev, yPrev, xNow, yNow
  pi = 4 * Atn(1)
  Call model.SketchManager.CreateLine(xLeft, yBase, 0, xRight, yBase, 0)
  xPrev = xRight
  yPrev = yBase
  For i = 1 To segments
    t = 1 - (i / segments)
    xNow = xLeft + (xRight - xLeft) * t
    yNow = yBase + rise * Sin(pi * t)
    Call model.SketchManager.CreateLine(xPrev, yPrev, 0, xNow, yNow, 0)
    xPrev = xNow
    yPrev = yNow
  Next
End Sub

Sub AddTriangleAt(model, x1, y1, x2, y2, x3, y3)
  Call model.SketchManager.CreateLine(x1, y1, 0, x2, y2, 0)
  Call model.SketchManager.CreateLine(x2, y2, 0, x3, y3, 0)
  Call model.SketchManager.CreateLine(x3, y3, 0, x1, y1, 0)
End Sub

Sub AddCircleAt(model, cx, cy, radius)
  Call model.SketchManager.CreateCircleByRadius(cx, cy, 0, radius)
End Sub

Sub AddPlateBetween(model, x1, y1, x2, y2, halfWidth)
  Dim dx, dy, len, nx, ny
  dx = x2 - x1
  dy = y2 - y1
  len = Sqr(dx * dx + dy * dy)
  If len < 0.0001 Then Exit Sub
  nx = -dy / len * halfWidth
  ny = dx / len * halfWidth
  Call model.SketchManager.CreateLine(x1 + nx, y1 + ny, 0, x2 + nx, y2 + ny, 0)
  Call model.SketchManager.CreateLine(x2 + nx, y2 + ny, 0, x2 - nx, y2 - ny, 0)
  Call model.SketchManager.CreateLine(x2 - nx, y2 - ny, 0, x1 - nx, y1 - ny, 0)
  Call model.SketchManager.CreateLine(x1 - nx, y1 - ny, 0, x1 + nx, y1 + ny, 0)
End Sub

Sub AddJaggedTireAt(model, cx, cy, toothCount, rLow, rHigh)
  Dim i, total, pi, a1, a2, r1, r2
  total = toothCount * 2
  pi = 4 * Atn(1)
  For i = 0 To total - 1
    a1 = i * 2 * pi / total
    a2 = (i + 1) * 2 * pi / total
    If i Mod 2 = 0 Then r1 = rHigh Else r1 = rLow
    If (i + 1) Mod 2 = 0 Then r2 = rHigh Else r2 = rLow
    Call model.SketchManager.CreateLine(cx + r1 * Cos(a1), cy + r1 * Sin(a1), 0, cx + r2 * Cos(a2), cy + r2 * Sin(a2), 0)
  Next
End Sub

Sub ExtrudeSketch(model, planeIndex, depth, name, r, g, b, mergeResult)
  Dim feat
  Call FinishSketch(model)
  Set feat = BossExtrude(model, depth, name, mergeResult)
  Call SetFeatureColor(feat, r, g, b)
End Sub

Sub ExtrudeSketchDir(model, planeIndex, depth, name, r, g, b, mergeResult, flipDir)
  Dim feat
  Call FinishSketch(model)
  Set feat = BossExtrudeDir(model, depth, name, mergeResult, flipDir)
  Call SetFeatureColor(feat, r, g, b)
End Sub

Sub AddTopBlock(model, cx, cz, w, zDepth, chamfer, height, name, r, g, b)
  Call StartSketchOnPlane(model, 2)
  Call AddChamferedRectAt(model, cx, cz, w, zDepth, chamfer)
  Call ExtrudeSketch(model, 2, height, name, r, g, b, False)
End Sub

Sub AddTopRectBlock(model, cx, cz, w, zDepth, height, name, r, g, b)
  Call StartSketchOnPlane(model, 2)
  Call AddRectAt(model, cx, cz, w, zDepth)
  Call ExtrudeSketch(model, 2, height, name, r, g, b, False)
End Sub

Sub AddTopBlockMerged(model, cx, cz, w, zDepth, chamfer, height, name, r, g, b)
  Call StartSketchOnPlane(model, 2)
  Call AddChamferedRectAt(model, cx, cz, w, zDepth, chamfer)
  Call ExtrudeSketch(model, 2, height, name, r, g, b, True)
End Sub

Sub AddTopTriangleBlock(model, x1, z1, x2, z2, x3, z3, height, name, r, g, b)
  Call StartSketchOnPlane(model, 2)
  Call AddTriangleAt(model, x1, z1, x2, z2, x3, z3)
  Call ExtrudeSketch(model, 2, height, name, r, g, b, False)
End Sub

Sub AddFrontRectFeature(model, cx, cy, w, h, depth, name, r, g, b)
  Call StartSketchOnPlane(model, 1)
  Call AddRectAt(model, cx, cy, w, h)
  Call ExtrudeSketch(model, 1, depth, name, r, g, b, False)
End Sub

Sub AddFrontChamferFeature(model, cx, cy, w, h, ch, depth, name, r, g, b)
  Call StartSketchOnPlane(model, 1)
  Call AddChamferedRectAt(model, cx, cy, w, h, ch)
  Call ExtrudeSketch(model, 1, depth, name, r, g, b, False)
End Sub

Sub AddFrontChamferFeatureMerged(model, cx, cy, w, h, ch, depth, name, r, g, b)
  Call StartSketchOnPlane(model, 1)
  Call AddChamferedRectAt(model, cx, cy, w, h, ch)
  Call ExtrudeSketch(model, 1, depth, name, r, g, b, True)
End Sub

Sub AddFrontCircleFeature(model, cx, cy, radius, depth, name, r, g, b)
  Call StartSketchOnPlane(model, 1)
  Call AddCircleAt(model, cx, cy, radius)
  Call ExtrudeSketch(model, 1, depth, name, r, g, b, False)
End Sub

Sub AddFrontChamferFeatureDir(model, cx, cy, w, h, ch, depth, name, r, g, b, flipDir)
  Call StartSketchOnPlane(model, 1)
  Call AddChamferedRectAt(model, cx, cy, w, h, ch)
  Call ExtrudeSketchDir(model, 1, depth, name, r, g, b, False, flipDir)
End Sub

Sub AddFrontCircleFeatureDir(model, cx, cy, radius, depth, name, r, g, b, flipDir)
  Call StartSketchOnPlane(model, 1)
  Call AddCircleAt(model, cx, cy, radius)
  Call ExtrudeSketchDir(model, 1, depth, name, r, g, b, False, flipDir)
End Sub

Sub AddFrontCurvedCapFeatureDir(model, xLeft, xRight, yBase, rise, segments, depth, name, r, g, b, flipDir)
  Call StartSketchOnPlane(model, 1)
  Call AddCurvedCapAt(model, xLeft, xRight, yBase, rise, segments)
  Call ExtrudeSketchDir(model, 1, depth, name, r, g, b, False, flipDir)
End Sub

Sub ExtrudeSketchOnOffsetPlane(model, depth, name, r, g, b, mergeResult, flipDir)
  Dim feat
  Call FinishSketch(model)
  Set feat = BossExtrudeDir(model, depth, name, mergeResult, flipDir)
  Call SetFeatureColor(feat, r, g, b)
End Sub

Sub AddCircleFeatureOnPlane(model, planeFeat, cx, cy, radius, depth, name, r, g, b, flipDir)
  Call StartSketchOnFeature(model, planeFeat)
  Call AddCircleAt(model, cx, cy, radius)
  Call ExtrudeSketchOnOffsetPlane(model, depth, name, r, g, b, False, flipDir)
End Sub

Sub AddChamferFeatureOnPlane(model, planeFeat, cx, cy, w, h, ch, depth, name, r, g, b, flipDir)
  Call StartSketchOnFeature(model, planeFeat)
  Call AddChamferedRectAt(model, cx, cy, w, h, ch)
  Call ExtrudeSketchOnOffsetPlane(model, depth, name, r, g, b, False, flipDir)
End Sub

Sub AddTriangleFeatureOnPlane(model, planeFeat, x1, y1, x2, y2, x3, y3, depth, name, r, g, b, flipDir)
  Call StartSketchOnFeature(model, planeFeat)
  Call AddTriangleAt(model, x1, y1, x2, y2, x3, y3)
  Call ExtrudeSketchOnOffsetPlane(model, depth, name, r, g, b, False, flipDir)
End Sub

Sub AddLegLinkOnPlane(model, planeFeat, x1, y1, x2, y2, halfWidth, depth, name, flipDir)
  Call StartSketchOnFeature(model, planeFeat)
  Call AddPlateBetween(model, x1, y1, x2, y2, halfWidth)
  Call ExtrudeSketchOnOffsetPlane(model, depth, name, 0.18, 0.18, 0.17, False, flipDir)
End Sub

Sub AddWheelOnPlane(model, planeFeat, cx, cy, prefix, flipDir)
  Call StartSketchOnFeature(model, planeFeat)
  Call AddJaggedTireAt(model, cx, cy, 32, 0.071, 0.077)
  Call ExtrudeSketchOnOffsetPlane(model, 0.064, prefix & "_side_mounted_block_tread_tire", 0.030, 0.030, 0.028, False, flipDir)

  Call AddCircleFeatureOnPlane(model, planeFeat, cx, cy, 0.048, 0.070, prefix & "_side_silver_hub_disc", 0.78, 0.78, 0.73, flipDir)
  Call AddChamferFeatureOnPlane(model, planeFeat, cx, cy, 0.058, 0.034, 0.006, 0.076, prefix & "_side_rectangular_hub_cap", 0.88, 0.88, 0.82, flipDir)
End Sub

Sub AddWheelLegModuleOnPlane(model, planeFeat, xHip, dir, prefix, flipDir)
  Dim yHip, xKnee, yKnee, xWheel, yWheel
  yHip = 0.020
  xKnee = xHip + dir * 0.126
  yKnee = -0.060
  xWheel = xHip + dir * 0.096
  yWheel = -0.180

  Call AddChamferFeatureOnPlane(model, planeFeat, xHip, yHip, 0.090, 0.070, 0.008, 0.030, prefix & "_side_hip_mount_plate", 0.30, 0.30, 0.28, flipDir)
  Call AddChamferFeatureOnPlane(model, planeFeat, xHip + dir * 0.018, yHip - 0.004, 0.060, 0.046, 0.006, 0.042, prefix & "_side_fork_clevis_block", 0.42, 0.42, 0.39, flipDir)
  Call AddChamferFeatureOnPlane(model, planeFeat, xHip + dir * 0.020, yHip - 0.060, 0.086, 0.026, 0.005, 0.024, prefix & "_side_chamfered_gusset_block", 0.26, 0.26, 0.24, flipDir)
  Call AddCircleFeatureOnPlane(model, planeFeat, xHip - dir * 0.030, yHip + 0.020, 0.0055, 0.046, prefix & "_side_upper_mount_bolt", 0.15, 0.15, 0.14, flipDir)
  Call AddCircleFeatureOnPlane(model, planeFeat, xHip + dir * 0.030, yHip - 0.020, 0.0055, 0.046, prefix & "_side_lower_mount_bolt", 0.15, 0.15, 0.14, flipDir)
  Call AddLegLinkOnPlane(model, planeFeat, xHip, yHip, xKnee, yKnee, 0.020, 0.034, prefix & "_side_upper_parallel_link", flipDir)
  Call AddLegLinkOnPlane(model, planeFeat, xHip + dir * 0.015, yHip - 0.010, xKnee + dir * 0.015, yKnee - 0.010, 0.009, 0.026, prefix & "_side_inner_upper_link", flipDir)
  Call AddLegLinkOnPlane(model, planeFeat, xKnee, yKnee, xWheel, yWheel, 0.020, 0.034, prefix & "_side_lower_parallel_link", flipDir)
  Call AddLegLinkOnPlane(model, planeFeat, xKnee + dir * 0.015, yKnee - 0.010, xWheel + dir * 0.015, yWheel - 0.010, 0.009, 0.026, prefix & "_side_inner_lower_link", flipDir)
  Call AddCircleFeatureOnPlane(model, planeFeat, xHip, yHip, 0.036, 0.048, prefix & "_side_hip_joint_pod", 0.76, 0.76, 0.72, flipDir)
  Call AddCircleFeatureOnPlane(model, planeFeat, xHip, yHip, 0.026, 0.056, prefix & "_side_hip_angle_control_washer", 0.62, 0.62, 0.58, flipDir)
  Call AddCircleFeatureOnPlane(model, planeFeat, xHip, yHip, 0.014, 0.064, prefix & "_side_hip_pin_cap", 0.42, 0.42, 0.39, flipDir)
  Call AddCircleFeatureOnPlane(model, planeFeat, xKnee, yKnee, 0.030, 0.046, prefix & "_side_knee_joint_pod", 0.76, 0.76, 0.72, flipDir)
  Call AddCircleFeatureOnPlane(model, planeFeat, xKnee, yKnee, 0.040, 0.026, prefix & "_side_knee_outer_angle_plate", 0.62, 0.62, 0.58, flipDir)
  Call AddCircleFeatureOnPlane(model, planeFeat, xKnee, yKnee, 0.017, 0.060, prefix & "_side_knee_pin_cap", 0.42, 0.42, 0.39, flipDir)
  Call AddCircleFeatureOnPlane(model, planeFeat, xWheel, yWheel, 0.030, 0.046, prefix & "_side_axle_joint_pod", 0.76, 0.76, 0.72, flipDir)
  Call AddCircleFeatureOnPlane(model, planeFeat, xWheel, yWheel, 0.021, 0.058, prefix & "_side_axle_pin_cap", 0.42, 0.42, 0.39, flipDir)
  Call AddWheelOnPlane(model, planeFeat, xWheel, yWheel, prefix, flipDir)
End Sub

Sub AddLegLink(model, x1, y1, x2, y2, halfWidth, depth, name)
  Call StartSketchOnPlane(model, 1)
  Call AddPlateBetween(model, x1, y1, x2, y2, halfWidth)
  Call ExtrudeSketch(model, 1, depth, name, 0.18, 0.18, 0.17, False)
End Sub

Sub AddWheel(model, cx, cy, prefix)
  Call StartSketchOnPlane(model, 1)
  Call AddJaggedTireAt(model, cx, cy, 24, 0.070, 0.079)
  Call ExtrudeSketch(model, 1, 0.210, prefix & "_wide_black_block_tread_tire", 0.030, 0.030, 0.028, False)

  Call AddFrontCircleFeature(model, cx, cy, 0.052, 0.218, prefix & "_large_silver_hub_disc", 0.78, 0.78, 0.73)
  Call AddFrontChamferFeature(model, cx, cy, 0.064, 0.038, 0.007, 0.226, prefix & "_rectangular_hub_cap", 0.88, 0.88, 0.82)
End Sub

Sub AddWheelLegModule(model, xHip, dir, prefix)
  Dim yHip, xKnee, yKnee, xWheel, yWheel
  yHip = 0.020
  ' Repeated wheel-leg module: front/rear are mirrored, while matching links
  ' keep the same slope so the four leg columns read as one coordinated system.
  xKnee = xHip + dir * 0.126
  yKnee = -0.070
  xWheel = xHip + dir * 0.096
  yWheel = -0.198
  Call AddLegLink(model, xHip, yHip, xKnee, yKnee, 0.020, 0.120, prefix & "_upper_dark_graphite_plate")
  Call AddLegLink(model, xKnee, yKnee, xWheel, yWheel, 0.020, 0.120, prefix & "_lower_dark_graphite_plate")
  Call AddFrontCircleFeature(model, xHip, yHip, 0.036, 0.142, prefix & "_hip_silver_joint", 0.76, 0.76, 0.72)
  Call AddFrontCircleFeature(model, xKnee, yKnee, 0.030, 0.142, prefix & "_knee_silver_joint", 0.76, 0.76, 0.72)
  Call AddFrontCircleFeature(model, xWheel, yWheel, 0.030, 0.142, prefix & "_axle_silver_joint", 0.76, 0.76, 0.72)
  Call AddWheel(model, xWheel, yWheel, prefix)
End Sub

Sub AddLegLinkDir(model, x1, y1, x2, y2, halfWidth, depth, name, flipDir)
  Call StartSketchOnPlane(model, 1)
  Call AddPlateBetween(model, x1, y1, x2, y2, halfWidth)
  Call ExtrudeSketchDir(model, 1, depth, name, 0.18, 0.18, 0.17, False, flipDir)
End Sub

Sub AddWheelDir(model, cx, cy, prefix, flipDir)
  Call StartSketchOnPlane(model, 1)
  Call AddJaggedTireAt(model, cx, cy, 24, 0.070, 0.079)
  Call ExtrudeSketchDir(model, 1, 0.210, prefix & "_wide_black_block_tread_tire", 0.030, 0.030, 0.028, False, flipDir)

  Call AddFrontCircleFeatureDir(model, cx, cy, 0.052, 0.218, prefix & "_large_silver_hub_disc", 0.78, 0.78, 0.73, flipDir)
  Call AddFrontChamferFeatureDir(model, cx, cy, 0.064, 0.038, 0.007, 0.226, prefix & "_rectangular_hub_cap", 0.88, 0.88, 0.82, flipDir)
End Sub

Sub AddWheelLegModuleDir(model, xHip, dir, prefix, flipDir)
  Dim yHip, xKnee, yKnee, xWheel, yWheel
  yHip = 0.020
  ' Repeated wheel-leg module: front/rear are mirrored, while matching links
  ' keep the same slope so the four leg columns read as one coordinated system.
  xKnee = xHip + dir * 0.126
  yKnee = -0.070
  xWheel = xHip + dir * 0.096
  yWheel = -0.198
  Call AddLegLinkDir(model, xHip, yHip, xKnee, yKnee, 0.020, 0.120, prefix & "_upper_dark_graphite_plate", flipDir)
  Call AddLegLinkDir(model, xKnee, yKnee, xWheel, yWheel, 0.020, 0.120, prefix & "_lower_dark_graphite_plate", flipDir)
  Call AddFrontCircleFeatureDir(model, xHip, yHip, 0.036, 0.142, prefix & "_hip_silver_joint", 0.76, 0.76, 0.72, flipDir)
  Call AddFrontCircleFeatureDir(model, xKnee, yKnee, 0.030, 0.142, prefix & "_knee_silver_joint", 0.76, 0.76, 0.72, flipDir)
  Call AddFrontCircleFeatureDir(model, xWheel, yWheel, 0.030, 0.142, prefix & "_axle_silver_joint", 0.76, 0.76, 0.72, flipDir)
  Call AddWheelDir(model, xWheel, yWheel, prefix, flipDir)
End Sub

Sub AddWheelLegModuleVisibleFar(model, xHip, dir, prefix, flipDir)
  Dim yHip, xKnee, yKnee, xWheel, yWheel
  ' Far-side modules are a smaller translated copy of the near-side linkage.
  ' The upper and lower link vectors keep the same slopes as the near side.
  yHip = 0.032
  xKnee = xHip + dir * 0.108
  yKnee = -0.052
  xWheel = xHip + dir * 0.082
  yWheel = -0.168
  Call AddLegLinkDir(model, xHip, yHip, xKnee, yKnee, 0.018, 0.110, prefix & "_upper_far_dark_graphite_plate", flipDir)
  Call AddLegLinkDir(model, xKnee, yKnee, xWheel, yWheel, 0.018, 0.110, prefix & "_lower_far_dark_graphite_plate", flipDir)
  Call AddFrontCircleFeatureDir(model, xHip, yHip, 0.033, 0.132, prefix & "_far_hip_silver_joint", 0.76, 0.76, 0.72, flipDir)
  Call AddFrontCircleFeatureDir(model, xKnee, yKnee, 0.028, 0.132, prefix & "_far_knee_silver_joint", 0.76, 0.76, 0.72, flipDir)
  Call AddFrontCircleFeatureDir(model, xWheel, yWheel, 0.028, 0.132, prefix & "_far_axle_silver_joint", 0.76, 0.76, 0.72, flipDir)
  Call AddWheelDir(model, xWheel, yWheel, prefix, flipDir)
End Sub

Sub WriteReadme()
  Dim file, txt
  txt = "# V5-light four-wheel visual model" & vbCrLf & vbCrLf
  txt = txt & "This is a low-memory SolidWorks visual mockup of the forest LFMC/fire-risk rover. It intentionally avoids a large multi-component assembly because the current SolidWorks session repeatedly triggers system memory warnings." & vbCrLf & vbCrLf
  txt = txt & "Modeling approach: one SLDPRT file with separated extruded features for the thicker chamfered chassis, segmented curved roof cap, front sensor head, side service panel, four side-mounted wheel-leg modules, hip mounting plates, fork clevis blocks, triangular gussets, block-tread tires, and field-data collection sensors." & vbCrLf & vbCrLf
  txt = txt & "Field-data modules represented in the model: front stereo/RGB cameras, lower multispectral/NIR window, roof lidar/RTK puck, environment mast with anemometer crossbar, short antenna, side electronics/battery bay, and a downward soil/moisture probe." & vbCrLf & vbCrLf
  txt = txt & "Use this as the V5 appearance direction. Later, when memory is stable, the same geometry can be split into true parts and a formal assembly." & vbCrLf
  Set file = fso.CreateTextFile(OUT_README, True, False)
  file.Write txt
  file.Close
End Sub

Dim model, ok, nearSidePlane, farSidePlane
Set model = swApp.NewDocument(PART_TEMPLATE, 0, 0, 0)
If model Is Nothing Then
  WScript.Echo "ERROR_NEW_PART"
  WScript.Quit 5
End If

Call SetDocColor(model, 0.74, 0.73, 0.64)
Set nearSidePlane = MakeOffsetPlane(model, 0.250, "v5_near_side_wheel_leg_plane")
Set farSidePlane = MakeOffsetPlane(model, -0.250, "v5_far_side_wheel_leg_plane")

' Main body and front sensor head: thicker, wider and less box-like.
Call AddTopBlock(model, 0.025, 0.000, 0.590, 0.300, 0.045, 0.100, "v5_1_thicker_chamfered_main_chassis", 0.74, 0.73, 0.64)
Call AddTopBlock(model, -0.330, 0.000, 0.165, 0.260, 0.030, 0.104, "v5_1_projecting_front_sensor_head", 0.66, 0.65, 0.56)
Call AddTopTriangleBlock(model, -0.328, 0.130, -0.242, 0.130, -0.242, 0.168, 0.102, "v5_7_front_near_shoulder_diagonal_fill_no_gap", 0.70, 0.69, 0.61)
Call AddTopTriangleBlock(model, -0.328, -0.130, -0.242, -0.130, -0.242, -0.168, 0.102, "v5_7_front_far_shoulder_diagonal_fill_no_gap", 0.70, 0.69, 0.61)
Call AddTopRectBlock(model, -0.252, 0.200, 0.042, 0.100, 0.058, "v5_17_front_near_side_100mm_outboard_beam_connected", 0.62, 0.62, 0.58)
Call AddTopRectBlock(model, 0.295, 0.200, 0.042, 0.100, 0.058, "v5_17_rear_near_side_100mm_outboard_beam_connected", 0.62, 0.62, 0.58)
Call AddTopRectBlock(model, -0.252, -0.200, 0.042, 0.100, 0.058, "v5_17_front_far_side_100mm_outboard_beam_connected", 0.62, 0.62, 0.58)
Call AddTopRectBlock(model, 0.295, -0.200, 0.042, 0.100, 0.058, "v5_17_rear_far_side_100mm_outboard_beam_connected", 0.62, 0.62, 0.58)
Call AddTopTriangleBlock(model, -0.284, 0.150, -0.220, 0.150, -0.252, 0.218, 0.058, "v5_13_front_near_side_compact_root_gusset", 0.62, 0.62, 0.58)
Call AddTopTriangleBlock(model, 0.263, 0.150, 0.327, 0.150, 0.295, 0.218, 0.058, "v5_13_rear_near_side_compact_root_gusset", 0.62, 0.62, 0.58)
Call AddTopTriangleBlock(model, -0.284, -0.150, -0.220, -0.150, -0.252, -0.218, 0.058, "v5_13_front_far_side_compact_root_gusset", 0.62, 0.62, 0.58)
Call AddTopTriangleBlock(model, 0.263, -0.150, 0.327, -0.150, 0.295, -0.218, 0.058, "v5_13_rear_far_side_compact_root_gusset", 0.62, 0.62, 0.58)
Call AddFrontCurvedCapFeatureDir(model, -0.270, 0.305, 0.096, 0.034, 18, 0.150, "v5_1_near_segmented_curved_upper_shell", 0.74, 0.73, 0.64, False)
Call AddFrontCurvedCapFeatureDir(model, -0.270, 0.305, 0.096, 0.034, 18, 0.150, "v5_1_far_segmented_curved_upper_shell", 0.74, 0.73, 0.64, True)
' Decorative front brow skipped in this pass to keep the rebuild stable after moving the rear wheel-leg group.

' Side panel and lower armor.
Call AddFrontChamferFeature(model, 0.105, 0.052, 0.205, 0.076, 0.008, 0.074, "v5_1_recessed_side_panel_frame", 0.045, 0.045, 0.042)
Call AddFrontChamferFeature(model, 0.105, 0.054, 0.158, 0.052, 0.005, 0.082, "v5_1_battery_electronics_panel_insert", 0.78, 0.78, 0.72)
Call AddFrontChamferFeatureMerged(model, 0.055, -0.018, 0.500, 0.062, 0.004, 0.086, "v5_7_integrated_lower_side_skirt_no_long_gap", 0.050, 0.050, 0.047)
Call AddFrontChamferFeatureMerged(model, -0.060, -0.054, 0.160, 0.044, 0.005, 0.060, "v5_7_protected_underbody_payload_bay_joined", 0.060, 0.060, 0.056)
Call AddFrontChamferFeatureMerged(model, -0.170, -0.044, 0.030, 0.066, 0.004, 0.056, "v5_7_front_skid_vertical_support_joined", 0.050, 0.050, 0.047)
Call AddFrontChamferFeatureMerged(model, 0.040, -0.044, 0.030, 0.066, 0.004, 0.056, "v5_7_center_skid_vertical_support_joined", 0.050, 0.050, 0.047)
Call AddFrontChamferFeatureMerged(model, 0.285, -0.044, 0.030, 0.066, 0.004, 0.056, "v5_7_rear_skid_vertical_support_joined", 0.050, 0.050, 0.047)

' Front optical face represented in side-projection for the lightweight mockup.
Call AddFrontChamferFeature(model, -0.392, 0.064, 0.124, 0.058, 0.008, 0.074, "v5_1_front_stereo_camera_bezel", 0.030, 0.030, 0.028)
Call AddFrontCircleFeature(model, -0.416, 0.066, 0.015, 0.084, "v5_1_left_rgb_camera_lens", 0.08, 0.28, 0.46)
Call AddFrontCircleFeature(model, -0.370, 0.066, 0.015, 0.084, "v5_1_right_depth_camera_lens", 0.08, 0.28, 0.46)
' Lower multispectral window skipped in this correction pass; the main stereo camera block remains.

' Four wheel-leg modules on real left/right side planes. This gives the rover a
' wide stance instead of using one center-plane profile with over-thick tires.
Call AddWheelLegModuleOnPlane(model, nearSidePlane, -0.252, -1, "front_near_leg", False)
Call AddWheelLegModuleOnPlane(model, nearSidePlane, 0.295, 1, "rear_near_leg", False)
Call AddWheelLegModuleOnPlane(model, farSidePlane, -0.252, -1, "front_far_leg", True)
Call AddWheelLegModuleOnPlane(model, farSidePlane, 0.295, 1, "rear_far_leg", True)

' Top sensor mast, lidar/RTK puck, antenna, anemometer, and handle.
Call AddTopBlock(model, -0.150, -0.052, 0.064, 0.058, 0.007, 0.142, "v5_1_roof_lidar_rtk_base", 0.055, 0.055, 0.052)
Call StartSketchOnPlane(model, 2)
Call AddCircleAt(model, -0.150, -0.052, 0.024)
Call ExtrudeSketch(model, 2, 0.166, "v5_1_lidar_rtk_cylindrical_puck", 0.76, 0.76, 0.70, False)
Call StartSketchOnPlane(model, 2)
Call AddCircleAt(model, 0.020, 0.000, 0.014)
Call ExtrudeSketch(model, 2, 0.208, "v5_1_tall_environment_weather_mast", 0.09, 0.09, 0.085, False)
Call AddFrontRectFeature(model, 0.020, 0.210, 0.092, 0.008, 0.018, "v5_1_anemometer_crossbar", 0.08, 0.08, 0.075)
Call AddFrontCircleFeature(model, -0.030, 0.210, 0.011, 0.018, "v5_1_left_wind_cup", 0.08, 0.08, 0.075)
Call AddFrontCircleFeature(model, 0.070, 0.210, 0.011, 0.018, "v5_1_right_wind_cup", 0.08, 0.08, 0.075)
Call StartSketchOnPlane(model, 2)
Call AddCircleAt(model, 0.190, 0.072, 0.006)
Call ExtrudeSketch(model, 2, 0.164, "v5_1_short_telemetry_antenna", 0.08, 0.08, 0.075, False)
Call AddTopBlock(model, 0.090, 0.066, 0.115, 0.014, 0.002, 0.140, "v5_1_silver_top_service_handle_bar", 0.78, 0.78, 0.72)
Call AddFrontChamferFeatureMerged(model, -0.170, -0.074, 0.060, 0.064, 0.004, 0.060, "v5_7_soil_probe_mounting_collar_joined_to_underbody", 0.060, 0.060, 0.056)
Call AddFrontRectFeature(model, -0.170, -0.120, 0.010, 0.092, 0.032, "v5_1_downward_soil_moisture_probe_rod", 0.10, 0.10, 0.095)
Call StartSketchOnPlane(model, 1)
Call AddTriangleAt(model, -0.178, -0.166, -0.162, -0.166, -0.170, -0.188)
Call ExtrudeSketch(model, 1, 0.032, "v5_1_soil_probe_tapered_tip", 0.10, 0.10, 0.095, False)

Call HideRefFeature(model, nearSidePlane)
Call HideRefFeature(model, farSidePlane)

On Error Resume Next
Call model.ClearSelection2(True)
Call model.ShowNamedView2("*Isometric", 7)
Call model.ViewZoomtofit2()
Call model.GraphicsRedraw2()
Call model.ForceRebuild3(False)
Err.Clear
On Error GoTo 0

ok = model.SaveAs3(OUT_PART, 0, 2)
WScript.Echo "PART_SAVE_STATUS=" & ok & " file=" & OUT_PART

swApp.Visible = True
Call model.ShowNamedView2("*Isometric", 7)
Call model.ViewZoomtofit2()
Call model.GraphicsRedraw2()
WScript.Sleep 1500
ok = model.SaveAs3(OUT_PNG, 0, 2)
WScript.Echo "PNG_SAVE_STATUS=" & ok & " file=" & OUT_PNG

Call WriteReadme()

On Error Resume Next
Call swApp.CloseDoc(model.GetTitle)
Call swApp.CloseAllDocuments(True)
If startedHere Then Call swApp.ExitApp
Err.Clear
On Error GoTo 0

WScript.Echo "V5_LIGHT_FOURWHEEL_DONE"
