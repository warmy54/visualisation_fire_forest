import vtk



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

    renderer.AddActor(renderStream(300,300,300,"data/output.14000.vti"))
    #renderer.AddVolume(volume)
    renderWindow.AddRenderer(whiteRender)

    
    # enter the rendering loop
    renderWindow.Render()
    renderWindowInteractor.Start()
    print("done")



def renderStream(x,y,z,file):
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
    
    data.GetPointData().SetVectors(merge.GetOutput().GetPointData().GetArray("combinationVector"))
    data.GetPointData().SetActiveVectors("combinationVector")

    streamline = vtk.vtkStreamTracer()
    streamline.DebugOn()
    streamline.SetInputData(data)
    streamline.SetStartPosition(x,y,z)
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


    streamLineActor = vtk.vtkActor()
    streamLineActor.SetMapper(mapper)
    streamLineActor.VisibilityOn();

    #streamLineActor.GetProperty().SetColor(1, 0, 0)  # Set the color to red

    return streamLineActor

main()