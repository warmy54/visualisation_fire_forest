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
    mapper = renderStreamMapper("data/output.14000.vti")

    streamLineActor = vtk.vtkActor()
    streamLineActor.SetMapper(mapper)
    streamLineActor.VisibilityOn();

    renderer.AddActor(streamLineActor)
    #renderer.AddVolume(volume)
    renderWindow.AddRenderer(whiteRender)

    
    # enter the rendering loop
    renderWindow.Render()
    renderWindowInteractor.Start()
    #print("done")

    

def renderStreamMapper(file):

    line1 = vtk.vtkLineSource()
    line1.SetResolution(80)
    line1.SetPoint1(0.0, 300.0, 220.0)
    line1.SetPoint2(0.0, -300.0, 220.0)

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
    streamline.SetSourceConnection(line1.GetOutputPort())
    streamline.SetIntegratorTypeToRungeKutta4()
    streamline.SetIntegrationDirectionToForward()
    streamline.Update()
    #print(data)
    #print(streamline)
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


if __name__ == "__main__":
    main()