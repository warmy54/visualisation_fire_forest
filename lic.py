import vtk


# Callback for the slider interaction
class vtkSliderCallback(object):
    def __init__(self, r_u, r_v, r_w):
        self.r_u = r_u
        self.r_v = r_v
        self.r_w = r_w

    def __call__(self, sliderWidget, eventId):
        self.r_u.SetResliceAxesOrigin(0, int(sliderWidget.GetRepresentation().GetValue()), 0)
        self.r_v.SetResliceAxesOrigin(0, int(sliderWidget.GetRepresentation().GetValue()), 0)
        self.r_w.SetResliceAxesOrigin(0, int(sliderWidget.GetRepresentation().GetValue()), 0)


def main():
    # ----------------------------------------------------------------
    # create the renderer and window interactor
    # ----------------------------------------------------------------
    renderWindow = vtk.vtkRenderWindow()
    renderWindow.SetSize(1200, 800)

    renderer = vtk.vtkRenderer()
    renderer.SetViewport(0, 0, 1.0, 1.0)
    renderer.SetBackground(1, 1, 1)
    renderWindow.AddRenderer(renderer)

    renderWindowInteractor = vtk.vtkRenderWindowInteractor()
    renderWindowInteractor.SetRenderWindow(renderWindow)

    # get renderer for the white background and interactor style
    whiteRender = vtk.vtkRenderer()
    whiteRender.SetViewport([1, 0, 1, 1])
    whiteRender.SetBackground([1, 1, 1])

    # ----------------------------------------------------------------
    # read the data set
    # ----------------------------------------------------------------
    reader = vtk.vtkXMLImageDataReader()
    reader.SetFileName("data/output.14000.vti")
    reader.Update()

    # vectorfield = vtk.vtkMergeVectorComponents()
    # vectorfield.SetInputConnection(reader.GetOutputPort())
    # vectorfield.SetInputArrayToProcess(0, 0, 0, 0, 'u')
    # vectorfield.SetInputArrayToProcess(1, 0, 0, 0, 'v')
    # vectorfield.SetInputArrayToProcess(2, 0, 0, 0, 'w')
    # vectorfield.SetXArrayName('u')
    # vectorfield.SetYArrayName('v')
    # vectorfield.SetZArrayName('w')
    # vectorfield.Update()

    reader.GetOutput().GetPointData().SetScalars(reader.GetOutput().GetPointData().GetArray('u'))

    # ----------------------------------------------------------------
    # Bulk Density of Dry Fuel
    # ----------------------------------------------------------------

    # subset = vtk.vtkExtractVOI()
    # subset.SetInputConnection(reader.GetOutputPort())
    # subset.SetVOI(0, 299, 0, 100, 0, 149)
    # subset.Update()

    # create a 2D slider
    sliderRep = vtk.vtkSliderRepresentation2D()
    sliderRep.SetMinimumValue(0)
    sliderRep.SetMaximumValue(249)
    sliderRep.SetValue(125)
    sliderRep.SetTitleText("Y-Extent")
    # set color properties
    sliderRep.GetSliderProperty().SetColor(0.2, 0.2, 0.6)  # Change the color of the knob that slides
    sliderRep.GetTitleProperty().SetColor(0, 0, 0)  # Change the color of the text indicating what the slider controls
    sliderRep.GetLabelProperty().SetColor(0, 0, 0.4)  # Change the color of the text displaying the value
    sliderRep.GetSelectedProperty().SetColor(0.4, 0.8, 0.4)  # Change the color of the knob when the mouse is held on it
    sliderRep.GetTubeProperty().SetColor(0.7, 0.7, 0.7)  # Change the color of the bar
    sliderRep.GetCapProperty().SetColor(0.7, 0.7, 0.7)  # Change the color of the ends of the bar
    # set position of the slider
    sliderRep.GetPoint1Coordinate().SetCoordinateSystemToDisplay()
    sliderRep.GetPoint1Coordinate().SetValue(40, 100)
    sliderRep.GetPoint2Coordinate().SetCoordinateSystemToDisplay()
    sliderRep.GetPoint2Coordinate().SetValue(200, 100)
    sliderWidget = vtk.vtkSliderWidget()
    sliderWidget.SetInteractor(renderWindowInteractor)
    sliderWidget.SetRepresentation(sliderRep)
    sliderWidget.SetAnimationModeToAnimate()

    reslice_u = vtk.vtkImageReslice()
    reslice_u.SetInputConnection(reader.GetOutputPort())
    reslice_u.SetOutputDimensionality(2)
    reslice_u.SetResliceAxesDirectionCosines(1, 0, 0, 0, 0, 1, 0, 1, 0)
    reslice_u.SetResliceAxesOrigin(0, 125, 0)
    reslice_u.Update()

    reader.GetOutput().GetPointData().SetScalars(reader.GetOutput().GetPointData().GetArray('v'))

    reslice_v = vtk.vtkImageReslice()
    reslice_v.SetInputConnection(reader.GetOutputPort())
    reslice_v.SetOutputDimensionality(2)
    reslice_v.SetResliceAxesDirectionCosines(1, 0, 0, 0, 0, 1, 0, 1, 0)
    reslice_v.SetResliceAxesOrigin(0, 125, 0)
    reslice_v.Update()

    reader.GetOutput().GetPointData().SetScalars(reader.GetOutput().GetPointData().GetArray('w'))

    reslice_w = vtk.vtkImageReslice()
    reslice_w.SetInputConnection(reader.GetOutputPort())
    reslice_w.SetOutputDimensionality(2)
    reslice_w.SetResliceAxesDirectionCosines(1, 0, 0, 0, 0, 1, 0, 1, 0)
    reslice_w.SetResliceAxesOrigin(0, 125, 0)
    reslice_w.Update()

    reader.GetOutput().GetPointData().SetScalars(reslice_u.GetOutput().GetPointData().GetArray('ImageScalars'))


    rename_u = vtk.vtkArrayRename()
    rename_u.SetInputConnection(reader.GetOutputPort())
    rename_u.SetArrayName(0, 8, "u_slice")
    rename_u.Update()

    rename_u.GetOutput().GetPointData().SetScalars(reslice_v.GetOutput().GetPointData().GetArray('ImageScalars'))

    rename_v = vtk.vtkArrayRename()
    rename_v.SetInputConnection(rename_u.GetOutputPort())
    rename_v.SetArrayName(0, 9, "v_slice")
    rename_v.Update()

    rename_v.GetOutput().GetPointData().SetScalars(reslice_w.GetOutput().GetPointData().GetArray('ImageScalars'))

    rename_w = vtk.vtkArrayRename()
    rename_w.SetInputConnection(rename_v.GetOutputPort())
    rename_w.SetArrayName(0, 10, "w_slice")
    rename_w.Update()

    vectorfield = vtk.vtkMergeVectorComponents()
    vectorfield.SetInputConnection(rename_w.GetOutputPort())
    vectorfield.SetInputArrayToProcess(0, 0, 0, 0, 'u_slice')
    vectorfield.SetInputArrayToProcess(1, 0, 0, 0, 'v_slice')
    vectorfield.SetInputArrayToProcess(2, 0, 0, 0, 'w_slice')
    vectorfield.SetXArrayName('u_slice')
    vectorfield.SetYArrayName('v_slice')
    vectorfield.SetZArrayName('w_slice')
    vectorfield.Update()

    # create the callback
    callback = vtkSliderCallback(reslice_u, reslice_v, reslice_w)
    sliderWidget.AddObserver("InteractionEvent", callback)
    sliderWidget.EnabledOn()

    # Create a threshold filter to select points with values above a threshold
    threshold = vtk.vtkThresholdPoints()
    threshold.SetInputConnection(reslice_u.GetOutputPort())
    threshold.ThresholdByUpper(0.2)
    threshold.Update()

    cylinderSource = vtk.vtkCylinderSource()
    cylinderSource.SetHeight(0.5)
    cylinderSource.SetRadius(0.1)
    cylinderSource.Update()

    transform = vtk.vtkTransform()
    transform.RotateX(90)
    transform.Update()

    transformFilter = vtk.vtkTransformPolyDataFilter()
    transformFilter.SetInputConnection(cylinderSource.GetOutputPort())
    transformFilter.SetTransform(transform)
    transformFilter.Update()

    glyph3D = vtk.vtkGlyph3D()
    glyph3D.SetInputConnection(threshold.GetOutputPort())
    glyph3D.SetSourceConnection(transformFilter.GetOutputPort())
    glyph3D.SetScaleModeToScaleByScalar()  # Map values to size of spheres
    glyph3D.SetScaleFactor(50)  # Set a default scaling factor
    glyph3D.Update()

    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(glyph3D.GetOutputPort())

    actor = vtk.vtkActor()
    actor.SetMapper(mapper)

    # ----------------------------------------------------------------
    # LIC
    # ----------------------------------------------------------------

    reslice_w.GetOutput().GetPointData().SetVectors(vectorfield.GetOutput().GetPointData().GetArray('combinationVector'))
    # reader.GetOutput().GetPointData().SetActiveVectors('combinationVector')
    # reader.Update()
    #
    print(reslice_w.GetOutput())
    #
    # print(reslice.GetOutput())

    lic = vtk.vtkImageDataLIC2D()
    lic.SetInputConnection(reslice_w.GetOutputPort())
    lic.SetSteps(500)
    lic.SetStepSize(0.1)
    lic.Update()

    mapper = vtk.vtkPolyDataMapper2D()
    mapper.SetInputConnection(lic.GetOutputPort())
    actor = vtk.vtkActor2D()
    actor.SetMapper(mapper)


    # add actor and renders
    renderer.AddActor(actor)
    renderWindow.AddRenderer(whiteRender)

    # enter the rendering loop
    renderWindow.Render()
    renderWindowInteractor.Start()


if __name__ == "__main__":
    main()