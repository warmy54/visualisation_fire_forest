from re import M
import vtk


# Callback for the slider interaction
class vtkSliderCallback(object):
    def __init__(self, seedline):
        self.seedline = seedline

    def __call__(self, sliderWidget, eventId):
        self.seedline.SetPoint1(0.0, 300.0, sliderWidget.GetRepresentation().GetValue())
        self.seedline.SetPoint2(0.0, -300.0, sliderWidget.GetRepresentation().GetValue())


# Render Window and Interactor
def getRendererRenderWindowAndInteractor(w, h):
    renderWindow = vtk.vtkRenderWindow()
    renderWindow.SetSize(w, h)

    renderer = vtk.vtkRenderer()
    renderer.SetViewport(0, 0, 1.0, 1.0)
    renderer.SetBackground(1, 1, 1)
    renderWindow.AddRenderer(renderer)

    renderWindowInteractor = vtk.vtkRenderWindowInteractor()
    renderWindowInteractor.SetRenderWindow(renderWindow)
    return renderer, renderWindow, renderWindowInteractor


# Streamlines
def getStreamLineMapper(reader, seedline):

    merge = vtk.vtkMergeVectorComponents()
    merge.SetInputConnection(reader.GetOutputPort())
    merge.SetInputArrayToProcess(0, 0, 0, 0, "u")
    merge.SetInputArrayToProcess(1, 0, 0, 0, "v")
    merge.SetInputArrayToProcess(2, 0, 0, 0, "w")
    merge.SetXArrayName("u")
    merge.SetYArrayName("v")
    merge.SetZArrayName("w")
    merge.Update()

    merge.GetOutput().GetPointData().SetVectors(merge.GetOutput().GetPointData().GetArray("combinationVector"))
    merge.GetOutput().GetPointData().SetActiveVectors("combinationVector")

    streamline = vtk.vtkStreamTracer()
    streamline.SetInputConnection(merge.GetOutputPort())
    streamline.SetSourceConnection(seedline.GetOutputPort())
    streamline.SetIntegratorTypeToRungeKutta4()
    streamline.SetMaximumPropagation(500)
    streamline.SetInitialIntegrationStep(0.1)
    streamline.SetIntegrationDirectionToBoth()
    streamline.Update()

    streamTube = vtk.vtkTubeFilter()
    streamTube.SetInputConnection(streamline.GetOutputPort())
    streamTube.SetRadius(0.02)
    streamTube.SetNumberOfSides(15)
    streamTube.SetVaryRadiusToVaryRadiusByVector()
    streamTube.Update()

    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(streamline.GetOutputPort())

    return mapper


# Bulk Density of Dry Fuel
def getDryFuelMapper(reader):
    # Set Scalar field
    reader.GetOutput().GetPointData().SetScalars(reader.GetOutput().GetPointData().GetArray('rhof_1'))
    reader.Update()

    # Create a threshold filter to select points with values above a threshold
    threshold = vtk.vtkThresholdPoints()
    threshold.SetInputConnection(reader.GetOutputPort())
    threshold.ThresholdByUpper(0.2)
    threshold.Update()

    # cylinder source to visualize dry fuel
    cylinderSource = vtk.vtkCylinderSource()
    cylinderSource.SetHeight(0.5)
    cylinderSource.SetRadius(0.1)
    cylinderSource.Update()

    # rotate cylinders
    transform = vtk.vtkTransform()
    transform.RotateX(90)
    transform.Update()

    # apply rotation
    transformFilter = vtk.vtkTransformPolyDataFilter()
    transformFilter.SetInputConnection(cylinderSource.GetOutputPort())
    transformFilter.SetTransform(transform)
    transformFilter.Update()

    # place cylinders on datapoints over threshold
    glyph3D = vtk.vtkGlyph3D()
    glyph3D.SetInputConnection(threshold.GetOutputPort())
    glyph3D.SetSourceConnection(transformFilter.GetOutputPort())
    glyph3D.SetScaleModeToScaleByScalar()  # Map values to size of spheres
    glyph3D.SetScaleFactor(50)  # Set a default scaling factor
    glyph3D.Update()

    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(glyph3D.GetOutputPort())

    return mapper


# Transfer function
def getTransferFunctionProperty():
    min_value = 310
    max_value = 900

    # transfer functions
    colorTransferFx = vtk.vtkColorTransferFunction()
    colorTransferFx.AddRGBPoint(min_value, 0.0, 0.0, 0.0)
    colorTransferFx.AddRGBPoint(315, 0.5, 0.5, 0.5)
    colorTransferFx.AddRGBPoint(390, 0.5, 0.5, 0.5)
    colorTransferFx.AddRGBPoint(400, 1, 0.5, 0.5)
    colorTransferFx.AddRGBPoint(max_value, 1.0, 0.0, 0.0)
    opacityTransferFx = vtk.vtkPiecewiseFunction()
    opacityTransferFx.AddPoint(min_value, 0.0)
    opacityTransferFx.AddPoint(315, 0.1)
    opacityTransferFx.AddPoint(390, 0.1)
    opacityTransferFx.AddPoint(450, 0.6)
    opacityTransferFx.AddPoint(max_value, 1.0)

    # assign transfer function to volume properties
    volumeProperty = vtk.vtkVolumeProperty()
    volumeProperty.SetColor(colorTransferFx)
    volumeProperty.SetScalarOpacity(opacityTransferFx)
    volumeProperty.ShadeOff()
    volumeProperty.SetInterpolationTypeToLinear()

    return volumeProperty;


# DirectVolume of Fire
def getFireMapper(reader):
    # Set scalar field
    reader.GetOutput().GetPointData().SetScalars(reader.GetOutput().GetPointData().GetArray('theta'))
    reader.Update()

    # raycast mapper
    rayCastMapper = vtk.vtkOpenGLGPUVolumeRayCastMapper()
    rayCastMapper.SetInputConnection(reader.GetOutputPort())
    return rayCastMapper


def getSlider():
    # create a 2D slider
    sliderRep = vtk.vtkSliderRepresentation2D()
    sliderRep.SetMinimumValue(200)
    sliderRep.SetMaximumValue(300)
    sliderRep.SetValue(210)
    sliderRep.SetTitleText("Seedline height")
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

    return sliderRep


def main():
    renderer, renderWindow, renderWindowInteractor = getRendererRenderWindowAndInteractor(1920, 1080)

    # read the data set
    reader = vtk.vtkXMLImageDataReader()
    name = "data/output.14000.vti"
    reader.SetFileName(name)
    reader.Update()

    # create slider for interactive seedline
    sliderWidget = vtk.vtkSliderWidget()
    sliderWidget.SetInteractor(renderWindowInteractor)
    sliderWidget.SetRepresentation(getSlider())

    # create seedline
    seedline = vtk.vtkLineSource()
    seedline.SetResolution(100)
    seedline.SetPoint1(0.0, 300.0, 210.0)
    seedline.SetPoint2(0.0, -300.0, 210.0)

    # create the callback
    callback = vtkSliderCallback(seedline)
    sliderWidget.AddObserver("InteractionEvent", callback)
    sliderWidget.EnabledOn()

    # create streamline actor
    streamLineActor = vtk.vtkActor()
    streamLineActor.SetMapper(getStreamLineMapper(reader, seedline))
    streamLineActor.VisibilityOn()

    # create dryfuel actor
    dryFuelActor = vtk.vtkActor()
    dryFuelActor.SetMapper(getDryFuelMapper(reader))

    # create fire volume
    fireVolume = vtk.vtkVolume()
    fireVolume.SetMapper(getFireMapper(reader))
    fireVolume.SetProperty(getTransferFunctionProperty())

    # choose camera angle
    camera = vtk.vtkCamera()
    camera.SetPosition(1700,0,1500)
    camera.SetFocalPoint(50,0,100)
    camera.Roll(270)
    camera.SetThickness(2500)
    renderer.SetActiveCamera(camera)


    # add actors and renders
    renderer.AddActor(dryFuelActor)
    renderer.AddVolume(fireVolume)
    renderer.AddActor(streamLineActor)
    
    # enter the rendering loop
    renderWindow.Render()
    renderWindowInteractor.Start()


if __name__ == "__main__":
    main()