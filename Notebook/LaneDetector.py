# Класс для обнаружения дорожной разметки
# и расчета радиуса кривизны дороги.
# Готова к работе!!!
# Перед запуском нужно настроить параметры под машинку.
import time
import numpy as np
import cv2


class LaneDetector(object):


    def __init__(self):
        self.time = None
        self.result = [0]
        self.road = False
        self.curvature = None
        self.position = None


    def color_threshold(self, image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        thresh_img = np.uint8(255.0 * gray / np.max(gray))
        thresh = (0, 120)
        bin = np.zeros_like(gray)
        bin[(thresh_img >= thresh[0]) & (thresh_img <= thresh[1])] = 255

        return bin


    def warp(self, img):
        rows, cols = img.shape[:2]

        points_in = np.float32([[212, 166], [402, 172], [57, 478], [535, 478]])     # Изменить!!!
        points_out = np.float32([[213, 166], [402, 172], [213, 478], [402, 478]])   # Изменить!!!

        M = cv2.getPerspectiveTransform(points_in, points_out)
        Mi = cv2.getPerspectiveTransform(points_out, points_in)

        img_warped = cv2.warpPerspective(img, M, (cols, rows), flags=cv2.INTER_LINEAR)

        return img_warped, Mi


    def get_histogram(self, bin_img):
        histogram = np.sum(bin_img[bin_img.shape[0] // 2:, :], axis=0)

        return histogram


    def slide_window(self, bin_img, histogram):
        black = np.zeros_like(bin_img)
        out_img = np.dstack((black, black, black))
        midpoint = np.int(histogram.shape[0] / 2)
        leftx_base = np.argmax(histogram[:midpoint])
        right_base = np.argmax(histogram[midpoint:]) + midpoint

        nwindows = 6
        window_height = np.int(bin_img.shape[0] / nwindows)
        nonzero = bin_img.nonzero()
        nonzero_y = np.array(nonzero[0])
        nonzero_x = np.array(nonzero[1])

        leftx_current = leftx_base
        rightx_current = right_base

        margin = 50
        minpix = 25

        left_lane_inds = []
        right_lane_inds = []
        for window in range(nwindows):
            y_low = bin_img.shape[0] - (window + 1) * window_height
            y_high = bin_img.shape[0] - window * window_height
            x_left_low = leftx_current - margin
            x_left_hight = leftx_current + margin
            x_right_low = rightx_current - margin
            x_right_hight = rightx_current + margin
            # cv2.rectangle(out_img, (x_left_low, y_low), (x_left_hight, y_high), (0, 255, 0), 2)
            # cv2.rectangle(out_img, (x_right_low, y_low), (x_right_hight, y_high), (0, 255, 0), 2)
            good_left_inds = ((nonzero_y >= y_low) & (nonzero_y <= y_high) & (nonzero_x >= x_left_low) & (
                    nonzero_x <= x_left_hight)).nonzero()[0]
            good_right_inds = ((nonzero_y >= y_low) & (nonzero_y <= y_high) & (nonzero_x >= x_right_low) & (
                    nonzero_x <= x_right_hight)).nonzero()[0]

            left_lane_inds.append(good_left_inds)
            right_lane_inds.append(good_right_inds)
            if len(good_left_inds) > minpix:
                leftx_current = np.int(np.mean(nonzero_x[good_left_inds]))

            if len(good_right_inds) > minpix:
                rightx_current = np.int(np.mean(nonzero_x[good_right_inds]))

        left_lane_inds = np.concatenate(left_lane_inds)
        right_lane_inds = np.concatenate(right_lane_inds)

        leftx = nonzero_x[left_lane_inds]
        lefty = nonzero_y[left_lane_inds]
        rightx = nonzero_x[right_lane_inds]
        righty = nonzero_y[right_lane_inds]

        left_fit = np.polyfit(lefty, leftx, 2)
        right_fit = np.polyfit(righty, rightx, 2)

        ploty = np.linspace(0, bin_img.shape[0] - 1, bin_img.shape[0])

        left_fitx = left_fit[0] * ploty ** 2 + left_fit[1] * ploty + left_fit[2]
        right_fitx = right_fit[0] * ploty ** 2 + right_fit[1] * ploty + right_fit[2]

        left_line = left_fit[2]
        right_line = right_fit[2]

        center = (left_line + right_line) / 2

        position = bin_img.shape[1] - center

        out_img[nonzero_y[left_lane_inds], nonzero_x[left_lane_inds]] = [0, 0, 255]
        out_img[nonzero_y[right_lane_inds], nonzero_x[right_lane_inds]] = [0, 0, 255]

        ret = {}
        ret['ploty'] = ploty
        ret['leftx'] = leftx
        ret['rightx'] = rightx
        ret['left_fitx'] = left_fitx
        ret['right_fitx'] = right_fitx

        return ret, out_img, position


    def calc_curvature(self, ret):
        ym_per_pix = 30.0 / 720   # Изменить!!!
        xm_per_pix = 3.7 / 700    # Изменить!!!

        leftx = ret['left_fitx'][::-1]
        rightx = ret['right_fitx'][::-1]
        mean_lane = np.mean(np.array([leftx, rightx]), axis=0)
        ploty = ret['ploty']
        y_eval = np.max(ploty)

        cr = np.polyfit(np.uint16(ploty * ym_per_pix), np.uint16(mean_lane * xm_per_pix), 2)
        curverad = ((1 + (2 * cr[0] * y_eval * ym_per_pix + cr[1]) ** 2) ** 1.5) / np.absolute(2 * cr[0])
        return curverad


    def draw_lane_lines(self, original_image, warped_image, Minv, draw_info):
        leftx = draw_info['leftx']
        rightx = draw_info['rightx']
        left_fitx = draw_info['left_fitx']
        right_fitx = draw_info['right_fitx']
        ploty = draw_info['ploty']

        warp_zero = np.zeros_like(warped_image).astype(np.uint8)
        color_warp = np.dstack((warp_zero, warp_zero, warp_zero))

        pts_left = np.array([np.transpose(np.vstack([left_fitx, ploty]))])
        pts_right = np.array([np.flipud(np.transpose(np.vstack([right_fitx, ploty])))])
        pts = np.hstack((pts_left, pts_right))

        cv2.fillPoly(color_warp, np.int_([pts]), (0, 255, 0))

        newwarp = cv2.warpPerspective(color_warp, Minv, (original_image.shape[1], original_image.shape[0]))
        result = cv2.addWeighted(original_image, 1, newwarp, 0.3, 0)

        return result


    def abs_diff(self, function):
        diff_func = []
        for i in range(function.shape[0] - 1):
            diff_func.append(abs(int(function[i + 1]) - int(function[i])))

            return (np.array(diff_func))


    def test_img(self, histogram):
        diff_histogram = self.abs_diff(histogram)
        print(np.max(diff_histogram))
        diff_threshold = np.zeros_like(diff_histogram)
        diff_threshold[diff_histogram > 3000] = 1
        if (np.sum(diff_threshold) > 3): return True
        return False


    def detect(self, image):
        thresh_img = self.color_threshold(image)
        warp_img, Mi = self.warp(thresh_img)
        histogram = self.get_histogram(warp_img)
        self.time = time.time()
        if (self.test_img(histogram)):
            self.road = True
            ret, img, self.position = self.slide_window(warp_img, histogram)
            self.curvature = self.calc_curvature(ret)
            self.result = self.draw_lane_lines(image, warp_img, Mi, ret)
        else:
            self.road = False
            self.position = None
            self.curvature = None
            self.result = image.copy()

            font = cv2.FONT_HERSHEY_SIMPLEX
            cv2.putText(self.result, 'No Road!', (self.result.shape[1] // 4, self.result.shape[0] // 2), font, 2,
                        (0, 0, 255), 2, cv2.LINE_AA)