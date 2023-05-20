import vtk



# Callback for the slider interaction
class vtkSliderCallback(object):
    def __init__(self, seedline):
        self.seedline = seedline

    def __call__(self, sliderWidget, eventId):
        self.seedline.SetPoint1(0.0, 300.0, sliderWidget.GetRepresentation().GetValue())
        self.seedline.SetPoint2(0.0, -300.0, sliderWidget.GetRepresentation().GetValue())


def main():
    

    renderWindow = vtk.vtkRenderWindow()
    renderWindow.SetSize(1200, 800)

    renderer = vtk.vtkRenderer()
    renderer.SetViewport(0, 0, 1.0, 1.0)
    renderer.SetBackground(10, 10, 10)
    renderWindow.AddRenderer(renderer)

    renderWindowInteractor = vtk.vtkRenderWindowInteractor()
    renderWindowInteractor.SetRenderWindow(renderWindow)

    # get renderer for the white background and interactor style
    whiteRender = vtk.vtkRenderer()
    whiteRender.SetViewport([1, 0, 1, 1])
    whiteRender.SetBackground([1, 1, 1])

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
    sliderWidget = vtk.vtkSliderWidget()
    sliderWidget.SetInteractor(renderWindowInteractor)
    sliderWidget.SetRepresentation(sliderRep)
    sliderWidget.SetAnimationModeToAnimate()

    seedline = vtk.vtkLineSource()
    seedline.SetResolution(100)
    seedline.SetPoint1(0.0, 300.0, 250.0)
    seedline.SetPoint2(0.0, -300.0, 250.0)

    # create the callback
    callback = vtkSliderCallback(seedline)
    sliderWidget.AddObserver("InteractionEvent", callback)
    sliderWidget.EnabledOn()

    # add actor and renders
    #renderer.AddActor(actor)
    step = 100
    #for x in range(0,5*step,step):
    #    for y in range(0,5*step,step):
    #        for z in range(0,5*step,step):
    #            renderer.AddActor(renderStream(x,y,z,"data/output.14000.vti"))
    #            print("i")
    #            print(x)
    #            print(y)
    #            print(z)
    mapper = renderStreamMapper(seedline, "data/output.14000.vti")

    streamLineActor = vtk.vtkActor()
    streamLineActor.SetMapper(mapper)
    streamLineActor.VisibilityOn();

    renderer.AddActor(streamLineActor)
    #renderer.AddVolume(volume)
    renderWindow.AddRenderer(whiteRender)

    
    # enter the rendering loop
    renderWindow.Render()
    renderWindowInteractor.Start()
    print("done")



def renderStreamMapper(seedline, file):

    #print(a)
    reader = vtk.vtkXMLImageDataReader()
    reader.SetFileName(file)

    u = reader.GetOutput().GetPointData().GetArray("u")
    v = reader.GetOutput().GetPointData().GetArray("v")
    w = reader.GetOutput().GetPointData().GetArray("w")

    


    merge = vtk.vtkMergeVectorComponents()
    merge.SetInputConnection(reader.GetOutputPort())
    merge.SetInputArrayToProcess(0, 0, 0, 0, "u")
    merge.SetInputArrayToProcess(1, 0, 0, 0, "v")
    merge.SetInputArrayToProcess(2, 0, 0, 0, "w")
    merge.SetXArrayName("u")
    merge.SetYArrayName("v")
    merge.SetZArrayName("w")
    merge.Update()

    data = vtk.vtkImageData()
    
    merge.GetOutput().GetPointData().SetVectors(merge.GetOutput().GetPointData().GetArray("combinationVector"))
    merge.GetOutput().GetPointData().SetActiveVectors("combinationVector")

    streamline = vtk.vtkStreamTracer()
    streamline.DebugOn()
    streamline.SetInputConnection(merge.GetOutputPort())
    streamline.SetSourceConnection(seedline.GetOutputPort())
    streamline.SetIntegratorTypeToRungeKutta4()
    streamline.SetIntegrationDirectionToForward()
    streamline.Update()
    print(data)
    print(streamline)
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


    #streamLineActor.GetProperty().SetColor(1, 0, 0)  # Set the color to red

    return mapper

main()