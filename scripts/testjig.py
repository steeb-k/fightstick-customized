import FreeCAD as App, Part, MeshPart, math
V=App.Vector
# board 96.3 x 45.31, holes (from board corner): x 4.176 / 92.138, y 4.126 / 41.074  -> 87.962 x 36.948 pattern
holes=[(4.176,4.126),(92.138,4.126),(92.138,41.074),(4.176,41.074)]
PL_T=2.0; PX,PY=100.0,49.0; ox,oy=(PX-96.3)/2,(PY-45.31)/2   # plate centred on the board outline
plate=Part.makeBox(PX,PY,PL_T)
# faint 0.4 mm recessed board outline on top of the plate as a visual reference (1 mm wide line)
outer=Part.makeBox(96.3,45.31,0.4,V(ox,oy,PL_T-0.4)); inner=Part.makeBox(94.3,43.31,0.5,V(ox+1,oy+1,PL_T-0.45))
plate=plate.cut(outer.cut(inner))
for hx,hy in holes:
    plate=plate.fuse(Part.makeCylinder(4.0,6.0,V(ox+hx,oy+hy,PL_T)))      # 8 mm post, 6 mm tall (same as shell)
    plate=plate.cut(Part.makeCylinder(2.0,5.0,V(ox+hx,oy+hy,PL_T+1.0)))   # 4 mm insert hole, 5 mm deep from post end
plate=plate.removeSplitter()
print("jig valid",plate.isValid(),"solids",len(plate.Solids),"bbox",plate.BoundBox)
c=[(round(f.Surface.Center.x-ox,3),round(f.Surface.Center.y-oy,3)) for f in plate.Faces if isinstance(f.Surface,Part.Cylinder) and abs(f.Surface.Radius-2.0)<1e-6]
print("hole centres rel. board corner:",sorted(set(c)))
m=MeshPart.meshFromShape(Shape=plate,LinearDeflection=0.02,AngularDeflection=math.radians(5),Relative=False)
print("mesh solid",m.isSolid(),"nonmanif",m.hasNonManifolds(),"selfint",m.hasSelfIntersections(),"facets",m.CountFacets)
m.write("/home/steeb/fightstick/GP2040_post_test_jig.stl"); print("written")
