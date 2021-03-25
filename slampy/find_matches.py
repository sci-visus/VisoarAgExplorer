
from OpenVisus import *
from slampy.image_utils import *

import cv2
import numpy

# /////////////////////////////////////////////////////////////////////////////////////


def DebugMatches(filename, width, height, img1, points1, H1, img2, points2, H2, TargetWidth=1024):

    def transformPoints(points, H):
        return cv2.perspectiveTransform(numpy.float32([points]), H)[0]

    def Scale(sx, sy):
        return numpy.array([[float(sx), 0.0, 0.0], [0.0, float(sy), 0.0], [0.0, 0.0, 1.0]])

    def Translate(tx, ty):
        return numpy.array([[1.0, 0.0, float(tx)], [0.0, 1.0, float(ty)], [0.0, 0.0, 1.0]])

    bounds1 = transformPoints(
        [(0, 0), (width, 0), (width, height), (0, height)], H1)
    bounds2 = transformPoints(
        [(0, 0), (width, 0), (width, height), (0, height)], H2)

    bounds = [*bounds1, *bounds2]

    border = 10
    x1 = int(min([x for x, y in bounds]))-border
    x2 = int(max([x for x, y in bounds]))+border
    y1 = int(min([y for x, y in bounds]))-border
    y2 = int(max([y for x, y in bounds]))+border

    W = x2 - x1
    H = y2 - y1
    vs = float(TargetWidth) / float(W)
    W = int(W * vs)
    H = int(H * vs)

    H1 = numpy.matmul(numpy.matmul(Scale(vs, vs), Translate(-x1, -y1)), H1)
    H2 = numpy.matmul(numpy.matmul(Scale(vs, vs), Translate(-x1, -y1)), H2)

    # could be that img1 and img2 are at a lower resolution
    Timg1 = numpy.matmul(
        H1, Scale(width / float(img1.shape[1]), height / float(img1.shape[0])))
    Timg2 = numpy.matmul(
        H2, Scale(width / float(img2.shape[1]), height / float(img2.shape[0])))
    # , cv2.INTER_LINEAR, cv2.BORDER_TRANSPARENT, (0, 0, 0, 0))
    blended1 = cv2.warpPerspective(img1, Timg1, (W, H))
    # , cv2.INTER_LINEAR, cv2.BORDER_TRANSPARENT, (0, 0, 0, 0))
    blended2 = cv2.warpPerspective(img2, Timg2, (W, H))

    img = numpy.zeros((H, W, 4), dtype='uint8')
    img[:, :, 3].fill(255)
    img[:, :, 0] = blended1
    img[:, :, 1] = blended2

    red = (0, 0, 255, 100)
    green = (0, 255, 0, 100)
    blue = (0, 0, 255, 100)
    points1 = transformPoints(points1, H1)
    points2 = transformPoints(points2, H2)
    for point1, point2 in zip(points1, points2):
        cv2.drawMarker(img, tuple(point1), red, cv2.MARKER_CROSS, 10, 2)
        cv2.drawMarker(img, tuple(point2), green, cv2.MARKER_CROSS, 10, 2)
        cv2.line(img, tuple(point1), tuple(point2), red,   3)
        cv2.line(img, tuple(point1), tuple(point2), green, 3)

    borders1 = transformPoints(
        [(0, 0), (width, 0), (width, height), (0, height)], H1)
    borders2 = transformPoints(
        [(0, 0), (width, 0), (width, height), (0, height)], H2)
    for I in range(4):
        cv2.line(img, tuple(borders1[I]), tuple(borders1[(I+1) % 4]), red,   2)
        cv2.line(img, tuple(borders2[I]), tuple(borders2[(I+1) % 4]), green, 2)

    img = cv2.flip(img, 0)
    SaveImage(filename, img)

# /////////////////////////////////////////////////////////////////////////////////////////


def RatioCheck(matches, ratio_check):
    return [match[0] for match in matches if len(match) > 1 and (match[0].distance / float(match[1].distance)) < ratio_check]


# /////////////////////////////////////////////////////////////////////////////////////////
def SymmetricCheck(matches1, matches2):
    ret = []
    for match1 in matches1:
        for match2 in matches2:
            if (match1.queryIdx == match2.trainIdx and match1.trainIdx == match2.queryIdx):
                ret.append(match1)
                break
    return ret

# //////////////////////////////////////////////////////////////////////////////////////////


def FindMatches(width, height,
                id1, points1, descriptors1,
                id2, points2, descriptors2,
                max_reproj_error, ratio_check):

    t1 = Time.now()

    out = ""
    out += "%d/%d" % (id1, id2)

    # cv2.FlannBasedMatcher matcher don't have advantages using flann
    matcher = cv2.BFMatcher(cv2.NORM_HAMMING)

    knn1 = matcher.knnMatch(descriptors1, descriptors2, 2)
    knn2 = matcher.knnMatch(descriptors2, descriptors1, 2)
    out += " knnMatch(%d,%d)" % (len(knn1), len(knn2))

    matches1 = RatioCheck(knn1, ratio_check)
    matches2 = RatioCheck(knn2, ratio_check)
    out += " matches1(%d) matches2(%d)" % (len(matches1), len(matches2))

    matches = SymmetricCheck(matches1, matches2)
    out += " SymmetricCheck(%d)" % (len(matches),)

    if not matches:
        out+"!matches"
        print(out)
        return ([], None, "!matches")

    points1 = [points1[match.queryIdx] for match in matches]
    points2 = [points2[match.trainIdx] for match in matches]

    H21 = None
    inliers = None
    try:
        H21, inliers = cv2.findHomography(
            numpy.float32(points1).reshape(-1, 1, 2),
            numpy.float32(points2).reshape(-1, 1, 2),
            cv2.RANSAC,
            max_reproj_error)
    except:
        print("error cv2 findHomography failed")

    if H21 is None:
        out += " !homo"
        print(out)
        return ([], None, "!homo")

    # keep only inliers
    inliers = inliers.ravel().tolist()
    matches = [matches[I] for I in range(len(matches)) if inliers[I]]
    out+"inliers(%d)" % (len(matches),)

    quad21 = Quad(Matrix(H21.ravel().tolist()), Quad(width, height))
    quad22 = Quad(width, height)

    if not quad21.isConvex():
        out += " notConvex"
        print(out)
        return (matches, H21, "notConvex")

    if quad21.wrongAngles():
        out += " wrongAngles"
        print(out)
        return (matches, H21, "wrongAngles")

    if (quad21.wrongScale(width, height)):
        out += " wrongScale"
        print(out)
        return (matches, H21, "wrongScale")

    out += " nmatches(%d) in %d msec" % (len(matches), t1.elapsedMsec())
    print(out)
    return (matches, H21, "")
