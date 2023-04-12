import vtk


def main():
    # This creates a polygonal cylinder model with eight circumferential facets
    # (i.e, in practice an octagonal prism).
    reader = vtk.vtkXMLImageDataReader()
    reader.SetFileName("./output.01000.vti")
    reader.Update()
    #reader.GetPointDataArraySelection().DisableAllArrays()
    name = reader.GetPointDataArraySelection().GetArrayName(5)
    reader.GetPointDataArraySelection().EnableArray(name)
    name = reader.GetPointDataArraySelection().GetArrayName(9)
    reader.GetPointDataArraySelection().EnableArray(name)
    name = reader.GetPointDataArraySelection().GetArrayName(10)
    #reader.GetPointDataArraySelection().EnableArray(name)
    reader.Update()
    print(reader.GetOutput())
    print(name)
    #filter = vtk.vtkPassSelectedArrays()
    #filter.SetInputData(reader.GetOutput())
    #filter.GetPointDataArraySelection().EnableAllArrays()
    #name = filter.GetPointDataArraySelection().GetArrayName(1)
    #filter.GetPointDataArraySelection().DisableAllArrays()
    #print(name)
    #filter.GetPointDataArraySelection().EnableArray(name)
    #filter.Update()
    #print(filter.GetOutput())

    surface = vtk.vtkMarchingCubes()
    surface.SetInputData(reader.GetOutput())
    #print(reader.GetOutput())
    surface.SetValue(0,400)

    mapper = vtk.vtkOpenGLPolyDataMapper()
    mapper.SetInputConnection(surface.GetOutputPort())
    mapper.ScalarVisibilityOff()

    actor = vtk.vtkActor()
    actor.SetMapper(mapper)

    renderer = vtk.vtkRenderer()
    renderer.SetBackground(1,1,255)
    renderer.AddActor(actor)

    renderWindow = vtk.vtkRenderWindow()
    renderWindow.SetSize(500,500)
    renderWindow.AddRenderer(renderer)

    renderWindowInteractor = vtk.vtkRenderWindowInteractor()
    renderWindowInteractor.SetRenderWindow(renderWindow)

    renderWindow.Render()
    renderWindowInteractor.Start()

if __name__ == "__main__":
    main()
