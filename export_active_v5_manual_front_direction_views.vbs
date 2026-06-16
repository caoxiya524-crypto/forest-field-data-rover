Option Explicit

Const OUT_DIR = "D:\data\pre_processing\solidworks_project\forest_lfmc_fire_rover_v5_light_fourwheel\views\manual_front_direction"
Const SNAPSHOT_PART = "D:\data\pre_processing\solidworks_project\forest_lfmc_fire_rover_v5_light_fourwheel\v5_light_fourwheel_visual_model_100_connected_manual_moved.SLDPRT"

Dim fso
Set fso = CreateObject("Scripting.FileSystemObject")
If Not fso.FolderExists("D:\data\pre_processing\solidworks_project\forest_lfmc_fire_rover_v5_light_fourwheel\views") Then
  fso.CreateFolder("D:\data\pre_processing\solidworks_project\forest_lfmc_fire_rover_v5_light_fourwheel\views")
End If
If Not fso.FolderExists(OUT_DIR) Then fso.CreateFolder(OUT_DIR)

Dim swApp
On Error Resume Next
Set swApp = GetObject(, "SldWorks.Application.33")
If Err.Number <> 0 Or swApp Is Nothing Then
  Err.Clear
  Set swApp = CreateObject("SldWorks.Application.33")
End If
On Error GoTo 0

If swApp Is Nothing Then
  WScript.Echo "SW_APP_FAILED"
  WScript.Quit 2
End If

swApp.Visible = True

Dim model
Set model = swApp.ActiveDoc
If model Is Nothing Then
  WScript.Echo "ACTIVE_DOC_NOT_FOUND"
  WScript.Quit 3
End If

Sub HideNamedRefFeature(model, featureName)
  Dim feat
  Set feat = model.FirstFeature
  Do While Not feat Is Nothing
    If feat.Name = featureName Then
      On Error Resume Next
      Call model.ClearSelection2(True)
      If feat.Select2(False, 0) Then
        Call swApp.RunCommand(895, "")
      End If
      Call model.ClearSelection2(True)
      Err.Clear
      On Error GoTo 0
      Exit Sub
    End If
    Set feat = feat.GetNextFeature
  Loop
End Sub

Sub PrepareDisplay(model)
  On Error Resume Next
  Call model.ClearSelection2(True)
  Call HideNamedRefFeature(model, "v5_near_side_wheel_leg_plane")
  Call HideNamedRefFeature(model, "v5_far_side_wheel_leg_plane")
  Call model.ViewDisplayShadedWithEdges()
  Call model.ViewZoomtofit2()
  Call model.GraphicsRedraw2()
  Err.Clear
  On Error GoTo 0
  WScript.Sleep 1200
End Sub

Sub ExportCurrent(model, fileName, label)
  Dim ok, outPath
  outPath = OUT_DIR & "\" & fileName
  Call PrepareDisplay(model)
  ok = model.SaveAs3(outPath, 0, 2)
  WScript.Echo "EXPORT_VIEW_STATUS=" & ok & " label=" & label & " file=" & outPath
End Sub

Sub ExportNamed(model, viewName, viewId, fileName, label)
  On Error Resume Next
  Call model.ShowNamedView2(viewName, viewId)
  Err.Clear
  On Error GoTo 0
  Call ExportCurrent(model, fileName, label)
End Sub

Dim saveOk
saveOk = model.SaveAs3(SNAPSHOT_PART, 0, 2)
WScript.Echo "SNAPSHOT_SAVE_STATUS=" & saveOk & " file=" & SNAPSHOT_PART

' Treat the user's current screen direction as the front/main view.
Call ExportCurrent(model, "manual_front_direction_front.png", "current_as_front")

' These are exported for orthographic checking after the current-direction front.
Call ExportNamed(model, "*Back", 2, "manual_front_direction_back_standard.png", "standard_back")
Call ExportNamed(model, "*Left", 3, "manual_front_direction_left_standard.png", "standard_left")
Call ExportNamed(model, "*Right", 4, "manual_front_direction_right_standard.png", "standard_right")
Call ExportNamed(model, "*Top", 5, "manual_front_direction_top_standard.png", "standard_top")
Call ExportNamed(model, "*Bottom", 6, "manual_front_direction_bottom_standard.png", "standard_bottom")
Call ExportNamed(model, "*Isometric", 7, "manual_front_direction_isometric.png", "standard_isometric")

WScript.Echo "ACTIVE_MANUAL_FRONT_DIRECTION_VIEWS_DONE"
