import vtk


# Callback for the slider interaction
class vtkSliderCallback(object):
    def __init__(self, ExtractVOI):
        self.ExtractVOI = ExtractVOI

    def __call__(self, sliderWidget, eventId):
        self.ExtractVOI.SetVOI(0, 299, 0, int(sliderWidget.GetRepresentation().GetValue()), 0, 149)

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

    vectorfield = vtk.vtkMergeVectorComponents()
    vectorfield.SetInputConnection(reader.GetOutputPort())
    vectorfield.SetInputArrayToProcess(0, 0, 0, 0, 'u')
    vectorfield.SetInputArrayToProcess(1, 0, 0, 0, 'v')
    vectorfield.SetInputArrayToProcess(2, 0, 0, 0, 'w')
    vectorfield.SetXArrayName('u')
    vectorfield.SetYArrayName('v')
    vectorfield.SetZArrayName('w')
    vectorfield.Update()

    reader.GetOutput().GetPointData().SetScalars(reader.GetOutput().GetPointData().GetArray('rhof_1'))

    # ----------------------------------------------------------------
    # Bulk Density of Dry Fuel
    # ----------------------------------------------------------------

    subset = vtk.vtkExtractVOI()
    subset.SetInputConnection(reader.GetOutputPort())
    subset.SetVOI(0, 299, 0, 100, 0, 149)
    subset.Update()

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

    # create the callback
    callback = vtkSliderCallback(subset)
    sliderWidget.AddObserver("InteractionEvent", callback)
    sliderWidget.EnabledOn()

    # Create a threshold filter to select points with values above a threshold
    threshold = vtk.vtkThresholdPoints()
    threshold.SetInputConnection(subset.GetOutputPort())
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

    reslice = vtk.vtkImageReslice()
    reslice.SetInputConnection(reader.GetOutputPort())
    reslice.SetOutputDimensionality(2)
    # reslice.SetInterpolationModeToLinear()
    reslice.SetResliceAxesDirectionCosines(1, 0, 0, 0, 0, 1, 0, 1, 0)
    reslice.SetResliceAxesOrigin(0, 125, 0)
    reslice.Update()

    reslice.GetOutput().GetPointData().SetVectors(vectorfield.GetOutput().GetPointData().GetArray('combinationVector'))
    print(reslice.GetOutput())
    reslice.GetOutput().GetPointData().SetActiveVectors('combinationVector')

    lic = vtk.vtkImageDataLIC2D()
    lic.SetInputConnection(reslice.GetOutputPort())
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