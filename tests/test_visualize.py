#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pathlib import Path
import warnings
import matplotlib
import pandas as pd
import pytest
from covsirphy import VisualizeBase, ColoredMap, LinePlot
from covsirphy import jpn_map
from covsirphy import Term


class TestVisualizeBase(object):
    def test_base(self):
        warnings.filterwarnings("ignore", category=UserWarning)
        with VisualizeBase() as vb:
            with pytest.raises(NotImplementedError):
                vb.plot()

    def test_file(self, imgfile):
        with VisualizeBase(filename=imgfile):
            pass
        assert Path(imgfile).exists()

    def test_setting(self, imgfile):
        with VisualizeBase(filename=imgfile) as vb:
            assert not vb.title
            assert isinstance(vb.ax, matplotlib.axes.Axes)
            vb.ax = vb.ax
            vb.title = "title"
            vb.tick_params(
                labelbottom=False, labelleft=False, left=False, bottom=False)


class TestColoredMap(object):
    def test_directory(self, imgfile):
        with ColoredMap(filename=imgfile) as cm:
            cm.directory = "input"
            assert cm.directory == "input"

    @pytest.mark.parametrize("variable", ["Infected"])
    def test_global_country(self, imgfile, jhu_data, variable):
        df = jhu_data.cleaned()
        df = df.loc[df[Term.PROVINCE] == Term.UNKNOWN]
        df = df.groupby(Term.COUNTRY).last().reset_index()
        df.rename(columns={variable: "Value"}, inplace=True)
        with ColoredMap(filename=imgfile) as cm:
            cm.plot(data=df, level=Term.COUNTRY)
        # Not with log10 scale
        with ColoredMap(filename=imgfile) as cm:
            cm.plot(data=df, level=Term.COUNTRY, logscale=False)

    @pytest.mark.parametrize("variable", ["Infected"])
    def test_global_country_ununique(self, imgfile, jhu_data, variable):
        df = jhu_data.cleaned()
        df = df.loc[df[Term.PROVINCE] == Term.UNKNOWN]
        df.rename(columns={variable: "Value"}, inplace=True)
        with pytest.raises(ValueError):
            with ColoredMap(filename=imgfile) as cm:
                cm.plot(data=df, level=Term.COUNTRY)

    @pytest.mark.parametrize("country", ["Japan", "United States", "China"])
    @pytest.mark.parametrize("variable", ["Infected"])
    def test_in_a_country(self, imgfile, jhu_data, country, variable):
        df = jhu_data.cleaned()
        df = df.loc[df[Term.COUNTRY] == country]
        df = df.loc[df[Term.PROVINCE] != Term.UNKNOWN]
        df = df.groupby(Term.PROVINCE).last().dropna().reset_index()
        df.rename(columns={variable: "Value"}, inplace=True)
        with ColoredMap(filename=imgfile) as cm:
            cm.plot(data=df, level=Term.PROVINCE)

    @pytest.mark.parametrize("variable", ["Infected"])
    def test_in_a_country_unselected_country(self, imgfile, jhu_data, variable):
        df = jhu_data.cleaned()
        df = df.loc[df[Term.PROVINCE] != Term.UNKNOWN]
        df = df.groupby(Term.PROVINCE).last().dropna().reset_index()
        df.rename(columns={variable: "Value"}, inplace=True)
        with pytest.raises(ValueError):
            with ColoredMap(filename=imgfile) as cm:
                cm.plot(data=df, level=Term.PROVINCE)

    @pytest.mark.parametrize("country", ["Japan"])
    @pytest.mark.parametrize("variable", ["Infected"])
    def test_in_a_country_ununique(self, imgfile, jhu_data, country, variable):
        df = jhu_data.cleaned()
        df = df.loc[df[Term.COUNTRY] == country]
        df = df.loc[df[Term.PROVINCE] != Term.UNKNOWN]
        df = df.dropna().reset_index()
        df.rename(columns={variable: "Value"}, inplace=True)
        with pytest.raises(ValueError):
            with ColoredMap(filename=imgfile) as cm:
                cm.plot(data=df, level=Term.PROVINCE)


class TestJapanMap(object):

    @pytest.mark.parametrize("variable", ["Infected"])
    def test_japan_map_display(self, jhu_data, variable):
        warnings.filterwarnings("ignore", category=UserWarning)
        warnings.filterwarnings("ignore", category=DeprecationWarning)
        df = jhu_data.cleaned()
        df = df.loc[(df[Term.COUNTRY] == "Japan") & (df[Term.PROVINCE] != "-")]
        df = df.groupby(Term.PROVINCE).last().reset_index().dropna()
        jpn_map(
            prefectures=df[Term.PROVINCE], values=df[variable],
            title="Japan: the number of {variable/lower()} cases"
        )

    @pytest.mark.parametrize("variable", ["Infected"])
    def test_japan_map(self, jhu_data, imgfile, variable):
        warnings.filterwarnings("ignore", category=DeprecationWarning)
        df = jhu_data.cleaned()
        df = df.loc[(df[Term.COUNTRY] == "Japan") & (df[Term.PROVINCE] != "-")]
        df = df.groupby(Term.PROVINCE).last().reset_index().dropna()
        jpn_map(
            prefectures=df[Term.PROVINCE], values=df[variable],
            title="Japan: the number of {variable.lower()} cases",
            filename=imgfile
        )


class TestLinePlot(object):
    def test_plot(self, jhu_data, imgfile):
        df = jhu_data.subset(country="Japan").set_index(Term.DATE)
        with LinePlot(filename=imgfile) as lp:
            lp.plot(data=df)
        with LinePlot(filename=imgfile) as lp:
            lp.plot(data=df, colormap="rainbow")
        with LinePlot(filename=imgfile) as lp:
            lp.plot(data=df, color_dict={Term.C: "blue"})
        with pytest.raises(ValueError):
            with LinePlot(filename=imgfile) as lp:
                lp.plot(data=df, colormap="unknown")

    def test_axis(self, jhu_data, imgfile):
        df = jhu_data.subset(country="Japan").set_index(Term.DATE)
        with LinePlot(filename=imgfile) as lp:
            lp.plot(data=df)
            lp.x_axis(x_logscale=True)
            lp.y_axis(y_logscale=True)
            lp.line(v=pd.Timestamp("01Jan2021"))
        with LinePlot(filename=imgfile) as lp:
            lp.plot(data=df)
            lp.y_axis(y_integer=True)
            lp.line(h=100_000)
