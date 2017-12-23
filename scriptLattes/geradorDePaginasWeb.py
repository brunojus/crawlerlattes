#!/usr/bin/python
# encoding: utf-8

from collections import defaultdict
import datetime
import os
import re
import unicodedata
import logging

import pandas
from pandas.core.indexing import IndexingError
from charts.graficoDeInternacionalizacao import *
from highcharts import *  # highcharts
import membro

logger = logging.getLogger('scriptLattes')


class GeradorDePaginasWeb:
    grupo = None
    dir = None
    version = None
    extensaoPagina = None
    arquivoRis = None

    def __init__(self, grupo):
        self.grupo = grupo
        self.version = 'V8.13'
        self.dir = self.grupo.obterParametro('global-diretorio_de_saida')

        if self.grupo.obterParametro('global-criar_paginas_jsp'):
            self.extensaoPagina = '.jsp'
            self.html1 = '<%@ page language="java" contentType="text/html; charset=ISO8859-1" pageEncoding="ISO8859-1"%> <%@ taglib prefix="f" uri="http://java.sun.com/jsf/core"%> <f:verbatim>'
            self.html2 = '</f:verbatim>'
        else:
            self.extensaoPagina = '.html'
            self.html1 = '<html>'
            self.html2 = '</html>'

        # geracao de arquivo RIS com as publicacoes
        if self.grupo.obterParametro('relatorio-salvar_publicacoes_em_formato_ris'):
            prefix = self.grupo.obterParametro('global-prefixo') + '-' if not self.grupo.obterParametro('global-prefixo') == '' else ''
            self.arquivoRis = open(self.dir + "/" + prefix + "publicacoes.ris", 'w')

        self.gerar_pagina_de_membros()
        #self.gerar_pagina_de_producao_qualificado_por_membro()
        self.gerarPaginasDeProducoesBibliograficas()


        if self.grupo.obterParametro('relatorio-incluir_internacionalizacao'):
            self.gerarPaginasDeInternacionalizacao()

        # final do fim!
        self.gerarPaginaPrincipal()

        if self.grupo.obterParametro('relatorio-salvar_publicacoes_em_formato_ris'):
            self.arquivoRis.close()


    def gerarPaginaPrincipal(self):
        nomeGrupo = self.grupo.obterParametro('global-nome_do_grupo').decode("utf8")

        s = self.html1 + ' \
        <head> \
           <title>' + nomeGrupo + '</title> \
           <meta name="Generator" content="scriptLattes"> \
           <link rel="stylesheet" href="css/scriptLattes.css" type="text/css">  \
           <meta http-equiv="Content-Type" content="text/html; charset=utf-8">'


        s += '</head> \n \
        <body onload="initialize()" onunload="GUnload()"> <div id="header">  \
        <center> <h2> ' + nomeGrupo + '</h2>'

        #| <a href=producao_membros' + self.extensaoPagina + '>Produção qualificado por membro</a> \
        s += '[ <a href=membros' + self.extensaoPagina + '><b>Membros</b></a> \
            | <a href=#producaoBibliografica>Produção bibliográfica</a>'.decode("utf8")

        if self.grupo.obterParametro('relatorio-mostrar_orientacoes'):
            s += '| <a href=#orientacoes>Orientações</a> '.decode("utf8")







        if self.grupo.obterParametro('relatorio-incluir_internacionalizacao'):
            s += '| <a href=#internacionalizacao>Internacionalização</a> '.decode("utf8")

        if self.grupo.obterParametro('relatorio-incluir_producao_com_colaboradores'):
            s += '| <a href=producao-com-colaboradores/index' + self.extensaoPagina + '><b>Produção com colaboradores</b></a> '.decode("utf8")

        s += ' ] </center><br></div>'
        s += '<h3 id="producaoBibliografica">Produção bibliográfica</h3> <ul>'.decode("utf8")

        if self.nPB0 > 0:
            s += '<li> <a href="PB0-0' + self.extensaoPagina + '">Artigos completos publicados em periódicos</a> '.decode(
                "utf8") + '(' + str(self.nPB0) + ')'
        if self.nPB4 > 0:
            s += '<li> <a href="PB4-0' + self.extensaoPagina + '">Trabalhos completos publicados em anais de congressos </a> '.decode(
                "utf8") + '(' + str(self.nPB4) + ')'
        if self.nPB5 > 0:
            s += '<li> <a href="PB5-0' + self.extensaoPagina + '">Resumos expandidos publicados em anais de congressos </a> '.decode(
                "utf8") + '(' + str(self.nPB5) + ')'
        if self.nPB6 > 0:
            s += '<li> <a href="PB6-0' + self.extensaoPagina + '">Resumos publicados em anais de congressos </a> '.decode(
                "utf8") + '(' + str(self.nPB6) + ')'
        if self.nPB > 0:
            s += '<li> <a href="PB-0' + self.extensaoPagina + '">Total de produção bibliográfica</a> '.decode(
                "utf8") + '(' + str(self.nPB) + ')'
        else:
            s += '<i>Nenhum item achado nos currículos Lattes</i>'.decode("utf8")



            # s+='</ul> <h3 id="patenteRegistro">Patente e Registro</h3> <ul>'.decode("utf8")
        #if self.nPR0>0:
        #	s+= '<li> <a href="PR0-0'+self.extensaoPagina+'">Patente</a> '.decode("utf8")+'('+str(self.nPR0)+')'
        # if self.nPR1>0:
        #	s+= '<li> <a href="PR1-0'+self.extensaoPagina+'">Programa de computador</a> '.decode("utf8")+'('+str(self.nPR1)+')'
        #if self.nPR2>0:
        #	s+= '<li> <a href="PR2-0'+self.extensaoPagina+'">Desenho industrial</a> '.decode("utf8")+'('+str(self.nPR2)+')'
        #if self.nPR0 == 0 and self.nPR1 == 0 and self.nPR2 == 0:
        #	s+= '<i>Nenhum item achado nos currículos Lattes</i>'.decode("utf8")



        if self.grupo.obterParametro('relatorio-mostrar_orientacoes'):
            s += '</ul> <h3 id="orientacoes">Orientações</h3> <ul>'.decode("utf8")
            s += '<li><b>Orientações em andamento</b>'.decode("utf8")
            s += '<ul>'
            if self.nOA0 > 0:
                s += '<li> <a href="OA0-0' + self.extensaoPagina + '">Supervisão de pós-doutorado</a> '.decode(
                    "utf8") + '(' + str(self.nOA0) + ')'
            if self.nOA1 > 0:
                s += '<li> <a href="OA1-0' + self.extensaoPagina + '">Tese de doutorado</a> '.decode(
                    "utf8") + '(' + str(self.nOA1) + ')'
            if self.nOA2 > 0:
                s += '<li> <a href="OA2-0' + self.extensaoPagina + '">Dissertação de mestrado</a> '.decode(
                    "utf8") + '(' + str(self.nOA2) + ')'
            if self.nOA3 > 0:
                s += '<li> <a href="OA3-0' + self.extensaoPagina + '">Monografia de conclusão de curso de aperfeiçoamento/especialização</a> '.decode(
                    "utf8") + '(' + str(self.nOA3) + ')'
            if self.nOA4 > 0:
                s += '<li> <a href="OA4-0' + self.extensaoPagina + '">Trabalho de conclusão de curso de graduação</a> '.decode(
                    "utf8") + '(' + str(self.nOA4) + ')'
            if self.nOA5 > 0:
                s += '<li> <a href="OA5-0' + self.extensaoPagina + '">Iniciação científica</a> '.decode(
                    "utf8") + '(' + str(self.nOA5) + ')'
            if self.nOA6 > 0:
                s += '<li> <a href="OA6-0' + self.extensaoPagina + '">Orientações de outra natureza</a> '.decode(
                    "utf8") + '(' + str(self.nOA6) + ')'
            if self.nOA > 0:
                s += '<li> <a href="OA-0' + self.extensaoPagina + '">Total de orientações em andamento</a> '.decode(
                    "utf8") + '(' + str(self.nOA) + ')'
            else:
                s += '<i>Nenhum item achado nos currículos Lattes</i>'.decode("utf8")
            s += '</ul>'

            s += '<li><b>Supervisões e orientações concluídas</b>'.decode("utf8")
            s += '<ul>'
            if self.nOC0 > 0:
                s += '<li> <a href="OC0-0' + self.extensaoPagina + '">Supervisão de pós-doutorado</a> '.decode(
                    "utf8") + '(' + str(self.nOC0) + ')'
            if self.nOC1 > 0:
                s += '<li> <a href="OC1-0' + self.extensaoPagina + '">Tese de doutorado</a> '.decode(
                    "utf8") + '(' + str(self.nOC1) + ')'
            if self.nOC2 > 0:
                s += '<li> <a href="OC2-0' + self.extensaoPagina + '">Dissertação de mestrado</a> '.decode(
                    "utf8") + '(' + str(self.nOC2) + ')'
            if self.nOC3 > 0:
                s += '<li> <a href="OC3-0' + self.extensaoPagina + '">Monografia de conclusão de curso de aperfeiçoamento/especialização</a> '.decode(
                    "utf8") + '(' + str(self.nOC3) + ')'
            if self.nOC4 > 0:
                s += '<li> <a href="OC4-0' + self.extensaoPagina + '">Trabalho de conclusão de curso de graduação</a> '.decode(
                    "utf8") + '(' + str(self.nOC4) + ')'
            if self.nOC5 > 0:
                s += '<li> <a href="OC5-0' + self.extensaoPagina + '">Iniciação científica</a> '.decode(
                    "utf8") + '(' + str(self.nOC5) + ')'
            if self.nOC6 > 0:
                s += '<li> <a href="OC6-0' + self.extensaoPagina + '">Orientações de outra natureza</a> '.decode(
                    "utf8") + '(' + str(self.nOC6) + ')'
            if self.nOC > 0:
                s += '<li> <a href="OC-0' + self.extensaoPagina + '">Total de orientações concluídas</a> '.decode(
                    "utf8") + '(' + str(self.nOC) + ')'
            else:
                s += '<i>Nenhum item achado nos currículos Lattes</i>'.decode("utf8")
            s += '</ul>'


        if self.grupo.obterParametro('relatorio-incluir_internacionalizacao'):
            s += '</ul> <h3 id="internacionalizacao">Internacionalização</h3> <ul>'.decode("utf8")
            if self.nIn0 > 0:
                s += '<li> <a href="In0-0' + self.extensaoPagina + '">Coautoria e internacionalização</a> '.decode(
                    "utf8") + '(' + str(self.nIn0) + ')'
            else:
                s += '<i>Nenhuma publicação com DOI disponível para análise</i>'.decode("utf8")
            s += '</ul>'


        self.salvarPagina("index" + self.extensaoPagina, s)


    def gerarPaginasDeProducoesBibliograficas(self):
        self.nPB0 = 0
        self.nPB4 = 0
        self.nPB5 = 0
        self.nPB6 = 0
        self.nPB = 0

        if self.grupo.obterParametro('relatorio-incluir_artigo_em_periodico'):
            self.nPB0 = self.gerar_pagina_de_producoes(self.grupo.compilador.listaCompletaArtigoEmPeriodico,
                                                       "Artigos completos publicados em periódicos", "PB0", ris=True)

        if self.grupo.obterParametro('relatorio-incluir_trabalho_completo_em_congresso'):
            self.nPB4 = self.gerar_pagina_de_producoes(self.grupo.compilador.listaCompletaTrabalhoCompletoEmCongresso,
                                                       "Trabalhos completos publicados em anais de congressos", "PB4",
                                                       ris=True)
        if self.grupo.obterParametro('relatorio-incluir_resumo_expandido_em_congresso'):
            self.nPB5 = self.gerar_pagina_de_producoes(self.grupo.compilador.listaCompletaResumoExpandidoEmCongresso,
                                                       "Resumos expandidos publicados em anais de congressos", "PB5",
                                                       ris=True)
        if self.grupo.obterParametro('relatorio-incluir_resumo_em_congresso'):
            self.nPB6 = self.gerar_pagina_de_producoes(self.grupo.compilador.listaCompletaResumoEmCongresso,
                                                       "Resumos publicados em anais de congressos", "PB6", ris=True)

        # Total de produção bibliográfica
        self.nPB = self.gerar_pagina_de_producoes(self.grupo.compilador.listaCompletaPB,
                                                  "Total de produção bibliográfica", "PB")


    def gerarPaginasDeInternacionalizacao(self):
        self.nIn0 = 0
        self.nIn0 = self.gerarPaginaDeInternacionalizacao(self.grupo.listaDePublicacoesEinternacionalizacao,
                                                          "Coautoria e internacionalização", "In0")

    @staticmethod
    def arranjar_publicacoes(listaCompleta):
        l = []
        for ano in sorted(listaCompleta.keys(), reverse=True):
            publicacoes = sorted(listaCompleta[ano], key=lambda x: x.chave.lower())
            for indice, publicacao in enumerate(publicacoes):
                l.append((ano, indice, publicacao))
        return l

    @staticmethod
    def chunks(lista, tamanho):
        ''' Retorna sucessivos chunks de 'tamanho' a partir da 'lista'
        '''
        for i in range(0, len(lista), tamanho):
            yield lista[i:i + tamanho]

    @staticmethod
    def template_pagina_de_producoes():
        st = u'''
                {top}
                {grafico}
                <h3>{titulo}</h3> <br>
                    <div id="container" style="min-width: 310px; max-width: 1920px; height: {height}; margin: 0"></div>
                    Número total de itens: {numero_itens}<br>

                    </table>

              '''
        return st

    @staticmethod
    def template_producao():
        s = u'''
            <tr valign="top"><td>{indice}. &nbsp;</td> <td>{publicacao}</td></tr>
            '''
        return s

    @staticmethod
    def gerar_grafico_de_producoes(listaCompleta, titulo):
        chart = highchart(type=chart_type.column)
        chart.set_y_title(u'Quantidade')
        # chart.set_x_title(u'Ano')
        # chart.set_x_categories(sorted(listaCompleta.keys()))
        # chart['xAxis']['type'] = 'categories'

        categories = []
        areas_map = {None: 0}
        estrato_area_ano_freq = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
        for ano, publicacoes in sorted(listaCompleta.items()):
            if ano!=0:
                categories.append(ano)
                for pub in publicacoes:
                    try:
                        #if not pub.qualis:
                        #    logger.debug("qualis is None")
                        estrato_area_ano_freq[None][None][ano] += 1  # sem qualis
                        #else:
                        #    if type(pub.qualis) is str:  # sem area
                        #        logger.debug("publicação com qualis string (sem área): '{}'".format(pub.qualis))
                        #    else:
                        #        for area, estrato in sorted(pub.qualis.items()):
                        #            estrato_area_ano_freq[estrato][area][ano] += 1
                        #            if area not in areas_map:
                        #                areas_map[area] = len(areas_map)
                    except AttributeError:
                        logger.debug(u"publicação sem atributo qualis")
                        estrato_area_ano_freq[None][None][ano] += 1  # producao que nao tem qualis

        series = []
        if not estrato_area_ano_freq.keys():  # produções vazias
            logger.debug("produções vazias")
        ###elif len(estrato_area_ano_freq.keys()) == 1 and None in estrato_area_ano_freq.keys():  # gráfico normal sem qualis
        else:  # gráfico normal sem qualis
            chart.settitle(titulo.decode('utf8'))
            chart['plotOptions']['column']['stacking'] = None
            chart['chart']['height'] = 300
            # chart['legend']['title'] = {'text': 'Ano'}
            chart['legend']['enabled'] = jscmd('false')
            chart['xAxis']['type'] = 'category'

            # freq = [estrato_area_ano_freq[None][None][ano] for ano in categories]
            # series.append({'name': u'Total', 'data': freq})
            # chart.set_x_categories(categories)

            data = []
            for ano in categories:
                freq = estrato_area_ano_freq[None][None][ano]
                data.append([ano, freq])
            series.append({'name': u'Total', 'data': data})

            # for ano, pub in sorted(listaCompleta.items()):
            #     series.append({'name': ano, 'data': [len(pub)]}) #, 'y': [len(pub)]})
        '''
        else:  # temos informações sobre qualis
            chart.settitle(u'Publicações por ano agrupadas por área e estrato Qualis')
            chart['chart']['type'] = 'bar'
            chart['chart']['height'] = 1080
            # chart['plotOptions']['column']['stacking'] = 'normal'
            chart['plotOptions']['bar']['stacking'] = 'normal'
            chart['legend']['title'] = {'text': 'Estrato Qualis'}
            chart['legend']['enabled'] = jscmd('true')
            chart['xAxis']['type'] = 'category'
            # chart['yAxis']['stackLabels']['rotation'] = 90
            # chart['yAxis']['stackLabels']['textAlign'] = 'right'

            drilldown_series = []
            for estrato, area_ano_freq in sorted(estrato_area_ano_freq.items()):
                if not estrato:
                    estrato = 'Sem Qualis'
                data = []
                # for area, ano_freq in area_ano_freq.items():
                for area in sorted(areas_map.keys()):
                    ano_freq = area_ano_freq[area]
                    freq = [ano_freq[ano] for ano in categories]
                    if not area:
                        area = u'Sem área'
                    data.append({'name': area, 'y': sum(freq), 'drilldown': area + estrato})

                    drilldown_series.append(
                        {'id': area + estrato, 'name': estrato, 'data': [[ano, ano_freq[ano]] for ano in categories]})
                one_serie = {'name': estrato, 'data': data}  #, 'stack': area}
                series.append(one_serie)
            chart['drilldown'] = {'series': drilldown_series}
        '''
        chart.set_series(series)

        return chart

    def gerar_pagina_de_producoes(self, lista_completa, titulo_pagina, prefixo, ris=False):

        total_producoes = sum(len(v) for v in lista_completa.values())

        keys = sorted(lista_completa.keys(), reverse=True)
        if keys:  # apenas geramos páginas web para lista com pelo menos 1 elemento
            max_elementos = int(self.grupo.obterParametro('global-itens_por_pagina'))
            total_paginas = int(math.ceil( total_producoes / (max_elementos * 1.0)))  # dividimos os relatórios em grupos (e.g 1000 items)

            grafico = self.gerar_grafico_de_producoes(lista_completa, titulo_pagina)  # FIXME: é o mesmo gráfico em todas as páginas

            anos_indices_publicacoes = self.arranjar_publicacoes(lista_completa)
            itens_por_pagina = self.chunks(anos_indices_publicacoes, max_elementos)
            for numero_pagina, itens in enumerate(itens_por_pagina):
                producoes_html = ''
                for indice_na_pagina, (ano, indice_no_ano, publicacao) in enumerate(itens):
                    # armazenamos uma copia da publicacao (formato RIS)
                    if ris and self.grupo.obterParametro('relatorio-salvar_publicacoes_em_formato_ris'):
                        self.salvarPublicacaoEmFormatoRIS(publicacao)

                    if indice_na_pagina == 0 or indice_no_ano == 0:
                        if indice_na_pagina > 0:
                            producoes_html += '</table></div>'
                        producoes_html += '<div id="dv-year-{0}"><h3 class="year">{0}</h3> <table>'.format(
                            ano if ano else '*itens sem ano')

                    producao_html = self.template_producao()
                    producao_html = producao_html.format(indice=indice_no_ano + 1,
                                                         publicacao=publicacao.html(self.grupo.listaDeMembros))
                    producoes_html += producao_html
                producoes_html += '</table></div>'

                pagina_html = self.template_pagina_de_producoes()
                pagina_html = pagina_html.format(top=self.pagina_top(),
                                                 grafico=grafico.html(), height=grafico['chart']['height'],
                                                 titulo=titulo_pagina.decode("utf8"), numero_itens=str(total_producoes))
                self.salvarPagina(prefixo + '-' + str(numero_pagina) + self.extensaoPagina, pagina_html)
        return total_producoes

    def gerarIndiceDePaginas(self, numeroDePaginas, numeroDePaginaAtual, prefixo):
        if numeroDePaginas == 1:
            return ''
        else:
            s = 'Página: '.decode("utf8")
            for i in range(0, numeroDePaginas):
                if i == numeroDePaginaAtual:
                    s += '<b>' + str(i + 1) + '</b> &nbsp;'
                else:
                    s += '<a href="' + prefixo + '-' + str(i) + self.extensaoPagina + '">' + str(i + 1) + '</a> &nbsp;'
            return '<center>' + s + '</center>'


    def gerarPaginaDeInternacionalizacao(self, listaCompleta, tituloPagina, prefixo):
        numeroTotalDeProducoes = 0
        gInternacionalizacao = GraficoDeInternacionalizacao(listaCompleta)
        htmlCharts = gInternacionalizacao.criarGraficoDeBarrasDeOcorrencias()

        keys = listaCompleta.keys()
        keys.sort(reverse=True)
        if len(keys) > 0:  # apenas geramos páginas web para lista com pelo menos 1 elemento
            for ano in keys:
                numeroTotalDeProducoes += len(listaCompleta[ano])

            maxElementos = int(self.grupo.obterParametro('global-itens_por_pagina'))
            numeroDePaginas = int(math.ceil(
                numeroTotalDeProducoes / (maxElementos * 1.0)))  # dividimos os relatórios em grupos (e.g 1000 items)

            numeroDeItem = 1
            numeroDePaginaAtual = 0
            s = ''

            for ano in keys:
                anoRotulo = str(ano) if not ano == 0 else '*itens sem ano'

                s += '<h3 class="year">' + anoRotulo + '</h3> <table>'

                elementos = listaCompleta[ano]
                elementos.sort(
                    key=lambda x: x.chave.lower())  # Ordenamos a lista em forma ascendente (hard to explain!)

                for index in range(0, len(elementos)):
                    pub = elementos[index]
                    s += '<tr valign="top"><td>' + str(index + 1) + '. &nbsp;</td> <td>' + pub.html() + '</td></tr>'

                    if numeroDeItem % maxElementos == 0 or numeroDeItem == numeroTotalDeProducoes:
                        st = self.pagina_top(cabecalho=htmlCharts)
                        st += '\n<h3>' + tituloPagina.decode(
                            "utf8") + '</h3> <br> <center> <table> <tr> <td valign="top"><div id="barchart_div"></div> </td> <td valign="top"><div id="geochart_div"></div> </td> </tr> </table> </center>'
                        st += '<table>'
                        st += '<tr><td>Número total de publicações realizadas SEM parceria com estrangeiros:</td><td>'.decode(
                            "utf8") + str(
                            gInternacionalizacao.numeroDePublicacoesRealizadasSemParceirasComEstrangeiros()) + '</td><td><i>(publicações realizadas só por pesquisadores brasileiros)</i></td></tr>'.decode(
                            "utf8")
                        st += '<tr><td>Número total de publicações realizadas COM parceria com estrangeiros:</td><td>'.decode(
                            "utf8") + str(
                            gInternacionalizacao.numeroDePublicacoesRealizadasComParceirasComEstrangeiros()) + '</td><td></td></tr>'
                        st += '<tr><td>Número total de publicações com parcerias NÂO identificadas:</td><td>'.decode(
                            "utf8") + str(
                            gInternacionalizacao.numeroDePublicacoesComParceriasNaoIdentificadas()) + '</td><td></td></tr>'
                        st += '<tr><td>Número total de publicações com DOI cadastrado:</td><td><b>'.decode(
                            "utf8") + str(numeroTotalDeProducoes) + '</b></td><td></td></tr>'
                        st += '</table>'
                        st += '<br> <font color="red">(*) A estimativa de "coautoria e internacionalização" é baseada na análise automática dos DOIs das publicações cadastradas nos CVs Lattes. A identificação de países, para cada publicação, é feita através de buscas simples de nomes de países.</font><br><p>'.decode(
                            "utf8")

                        st += self.gerarIndiceDePaginas(numeroDePaginas, numeroDePaginaAtual, prefixo)
                        st += s  #.decode("utf8")
                        st += '</table>'


                        self.salvarPagina(prefixo + '-' + str(numeroDePaginaAtual) + self.extensaoPagina, st)
                        numeroDePaginaAtual += 1

                        if (index + 1) < len(elementos):
                            s = '<h3 class="year">' + anoRotulo + '</h3> <table>'
                        else:
                            s = ''
                    numeroDeItem += 1

                s += '</table>'
        return numeroTotalDeProducoes




    @staticmethod
    def producao_qualis(elemento, membro):
        tabela_template = u"<table style=\"width: 100%; display: block; overflow-x: auto;\"><tbody>" \
                          u"<br><span style=\"font-size:14px;\"><b>Totais de publicações com Qualis:</b></span><br><br>" \
                          u"<div style=\"width:100%; overflow-x:scroll;\">{body}</div>" \
                          u"</tbody></table>"

        first_column_template = u'<div style="float:left; width:200px; height: auto; border: 1px solid black; border-collapse: collapse; margin-left:0px; margin-top:0px;' \
                                ' background:#CCC; vertical-align: middle; padding: 4px 0; {extra_style}"><b>{header}</b></div>'
        header_template = u'<div style="float:left; width:{width}px; height: auto; border-style: solid; border-color: black; border-width: 1 1 1 0; border-collapse: collapse; margin-left:0px; margin-top:0px;' \
                          ' background:#CCC; text-align: center; vertical-align: middle; padding: 4px 0;"><b>{header}</b></div>'
        line_template = u'<div style="float:left; width:{width}px; height: auto; border-style: solid; border-color: black; border-width: 1 1 1 0; border-collapse: collapse; margin-left:0px; margin-top:0px;' \
                        ' background:#EAEAEA; text-align: center; vertical-align: middle; padding: 4px 0;">{value}</div>'  # padding:4px 6px;

        cell_size = 40
        num_estratos = len(membro.tabela_qualis['estrato'].unique())

        header_ano = first_column_template.format(header='Ano', extra_style='text-align: center;')
        header_estrato = first_column_template.format(header=u'Área \\ Estrato', extra_style='text-align: center;')

        for ano in sorted(membro.tabela_qualis['ano'].unique()):
            header_ano += header_template.format(header=ano, width=num_estratos * (cell_size + 1) - 1)
            for estrato in sorted(membro.tabela_qualis['estrato'].unique()):
                header_estrato += header_template.format(header=estrato, width=cell_size)

        if membro.tabela_qualis and not membro.tabela_qualis.empty():
            pt = membro.tabela_qualis.pivot_table(columns=['area', 'ano', 'estrato'], values='freq')
        lines = ''
        for area in sorted(membro.tabela_qualis['area'].unique()):
            lines += first_column_template.format(header=area, extra_style='')
            for ano in sorted(membro.tabela_qualis['ano'].unique()):
                for estrato in sorted(membro.tabela_qualis['estrato'].unique()):
                    try:
                        lines += line_template.format(value=pt.ix[area, ano, estrato], width=cell_size)
                    except IndexingError:
                        lines += line_template.format(value='&nbsp;', width=cell_size)
            lines += '<div style="clear:both"></div>'

        tabela_body = header_ano
        tabela_body += '<div style="clear:both"></div>'
        tabela_body += header_estrato
        tabela_body += '<div style="clear:both"></div>'
        tabela_body += lines

        tabela = tabela_template.format(body=tabela_body)

        # first = True
        # # FIXME: considerar as áreas
        # for ano in sorted(membro.tabela_qualis['ano'].unique()):
        #     if first:
        #         first = False
        #         display = "block"
        #     else:
        #         display = "none"
        #
        #     # esquerda = '<a class="ano_esquerda" rel="{ano}" rev="{rev}" style="cursor:pointer; padding:2px; border:1px solid #C3FDB8;">«</a>'.format(
        #     #     ano=ano, rev=str(elemento))
        #     # direita = '<a class="ano_direita" rel="{ano}" rev="{rev}" style="cursor:pointer; padding:2px; border:1px solid #C3FDB8;">«</a>'.format(
        #     #     ano=ano, rev=str(elemento))
        #     # tabela += '<div id="ano_{ano}_{elemento}" style="display: {display}">{esquerda}<b>{ano}</b>{direita}<br/><br/>'.format(
        #     #           ano=ano, elemento=elemento, display=display, esquerda=esquerda, direita=direita)
        #     chaves = ''
        #     valores = ''
        #
        #     for tipo, frequencia in membro.tabelaQualisDosAnos[ano].items():
        #         # FIXME: terminar de refatorar
        #         if tipo == "Qualis nao identificado":
        #             tipo = '<span title="Qualis nao identificado">QNI</span>'
        #
        #         chaves += '<div style="float:left; width:70px; border:1px solid #000; margin-left:-1px; margin-top:-1px; background:#CCC; padding:4px 6px;"><b>' + str(
        #             tipo) + '</b></div>'
        #         valores += '<div style="float:left; width:70px; border:1px solid #000; margin-left:-1px; margin-top:-1px; background:#EAEAEA; padding:4px 6px;">' + str(
        #             frequencia) + '</div>'
        #
        #     tabela += '<div>' + chaves + '</div>'
        #     tabela += '<div style="clear:both"></div>'
        #     tabela += '<div>' + valores + '</div>'
        #     tabela += '<div style="clear:both"></div>'
        #     tabela += "<br><br></div>"
        # tabTipo += '<div>'
        # chaves = ''
        # valores = ''
        # for chave, valor in membro.tabelaQualisDosTipos.items():
        #
        #     if (chave == "Qualis nao identificado"):
        #         chave = "QNI"
        #
        #     chaves += '<div style="float:left; width:70px; border:1px solid #000; margin-left:-1px; margin-top:-1px; background:#CCC; padding:4px 6px;"><b>' + str(
        #         chave) + '</b></div>'
        #     valores += '<div style="float:left; width:70px; border:1px solid #000; margin-left:-1px; margin-top:-1px; background:#EAEAEA; padding:4px 6px;">' + str(
        #         valor) + '</div>'
        # tabTipo += '<div>' + chaves + '</div>'
        # tabTipo += '<div style="clear:both"></div>'
        # tabTipo += '<div>' + valores + '</div>'
        # tabTipo += '<div style="clear:both"></div>'
        # tabTipo += "<br><br></div><br><br>"
        return tabela

    def gerar_pagina_de_membros(self):
        s = self.pagina_top()
        #s += u'\n<h3>Lista de membros</h3> <table id="membros" class="collapse-box" ><tr>\
        s += u'\n<h3>Lista de membros</h3> <table id="membros" class="sortable" ><tr>\
                <th></th>\
                <th></th>\
                <th><b><font size=-1>Rótulo/Grupo</font></b></th>\
                <th><b><font size=-1>Bolsa CNPq</font></b></th>\
                <th><b><font size=-1>Período de<br>análise individual</font></b></th>\
                <th><b><font size=-1>Data de<br>atualização do CV</font><b></th>\
                <th><b><font size=-1>Grande área</font><b></th>\
                <th><b><font size=-1>Área</font><b></th>\
                <th><b><font size=-1>Instituição</font><b></th>\
                </tr>'

        elemento = 0
        for membro in self.grupo.listaDeMembros:
            elemento    += 1
            bolsa        = membro.bolsaProdutividade  if membro.bolsaProdutividade else ''
            rotulo       = membro.rotulo if not membro.rotulo == '[Sem rotulo]' else ''
            rotulo       = rotulo.decode('iso-8859-1', 'replace')
            nomeCompleto = unicodedata.normalize('NFKD', membro.nomeCompleto).encode('ASCII', 'ignore')

            self.gerar_pagina_individual_de_membro(membro)

            #print " --------------------------------------------"
            #print membro.nomeCompleto
            #print type(membro.nomeCompleto)
            #print " "
            #nomeCompleto = membro.nomeCompleto.decode('utf8','replace')
            #print nomeCompleto
            #print type(nomeCompleto)
            #print " --------------------------------------------"
            #nomeCompleto = membro.nomeCompleto.decode('iso-8859-1','replace')

            # html_qualis = self.producao_qualis(elemento, membro)
            ##         <td valign="center" height="40px">' + str(elemento) + '.</td> \
            ##        <td valign="top" height="40px"><img src="' + membro.foto + '" width="40px"></td> \

            s += u'\n<tr class="testetabela"> \
                     <td valign="center">{0}.</td> \
                     <td>{2}</td> \
                     <td><font size=-2>{3}</font></td> \
                     <td><font size=-2>{4}</font></td> \
                     <td><font size=-2>{5}</font></td> \
                     <td><font size=-2>{6}</font></td> \
                     <td><font size=-2>{7}</font></td> \
                     <td><font size=-2>{8}</font></td> \
                     <td><font size=-2>{9}</font></td> \
                 </tr>'.format(str(elemento),
                         membro.idLattes,
                         nomeCompleto,
                         rotulo,
                         bolsa,
                         membro.periodo,
                         membro.atualizacaoCV,
                         membro.nomePrimeiraGrandeArea,
                         membro.nomePrimeiraArea,
                         membro.instituicao)


        s += '\n</table>'


        s += '<script>' \
             '  $(document).ready( function () {' \
             '    $(\'#membros\').DataTable();' \
             '  });' \
             '</script>'





        self.salvarPagina("membros" + self.extensaoPagina, s)

    def gerar_pagina_individual_de_membro(self, membro):
        bolsa        = membro.bolsaProdutividade  if membro.bolsaProdutividade else ''
        rotulo       = membro.rotulo if not membro.rotulo == '[Sem rotulo]' else ''
        rotulo       = rotulo.decode('iso-8859-1', 'replace')
        nomeCompleto = unicodedata.normalize('NFKD', membro.nomeCompleto).encode('ASCII', 'ignore')

        s = self.pagina_top()
        s += u'\n<h3>{0}</h3>\
                <br><p>\
                <table border=0>\
                <tr><td>\
                </td><td>\
                    <ul>\
                    <li> <b>Atualização</b> {1}</li>\
                    </ul>\
                </td><tr>\
                </table><br>'.format(nomeCompleto,

                        membro.atualizacaoCV)

        (nPB0, lista_PB0, titulo_PB0) = self.gerar_lista_de_producoes_de_membro( membro.listaArtigoEmPeriodico, u"Artigos completos publicados em periódicos" )
        (nPB4, lista_PB4, titulo_PB4) = self.gerar_lista_de_producoes_de_membro( membro.listaTrabalhoCompletoEmCongresso, u"Trabalhos completos publicados em anais de congressos" )
        (nPB5, lista_PB5, titulo_PB5) = self.gerar_lista_de_producoes_de_membro( membro.listaResumoExpandidoEmCongresso, u"Resumos expandidos publicados em anais de congressos" )
        (nPB6, lista_PB6, titulo_PB6) = self.gerar_lista_de_producoes_de_membro( membro.listaResumoEmCongresso, u"Resumos publicados em anais de congressos" )




        (nCE, lista_CE, titulo_CE, lista_CE_detalhe)    = self.gerar_lista_de_colaboracoes (membro, u'Colaborações endôgenas')

        s += u'<h3>Produção bibliográfica</h3> <ul>'
        s += u'<li><a href="#{}">{}</a> ({}) </li>'.format( 'PB0', titulo_PB0, nPB0 )
        s += u'<li><a href="#{}">{}</a> ({}) </li>'.format( 'PB4', titulo_PB4, nPB4 )
        s += u'<li><a href="#{}">{}</a> ({}) </li>'.format( 'PB5', titulo_PB5, nPB5 )
        s += u'<li><a href="#{}">{}</a> ({}) </li>'.format( 'PB6', titulo_PB6, nPB6 )
        s += u'</ul>'


        s += u'<hr>'
        s += u'<h3>Produção bibliográfica</h3> <ul>'
        s += u'<li id="{}"> <b>{}</b> ({}) <br> {} </li>'.format( 'PB0', titulo_PB0, nPB0, lista_PB0)
        s += u'<li id="{}"> <b>{}</b> ({}) <br> {} </li>'.format( 'PB4', titulo_PB4, nPB4, lista_PB4)
        s += u'<li id="{}"> <b>{}</b> ({}) <br> {} </li>'.format( 'PB5', titulo_PB5, nPB5, lista_PB5)
        s += u'<li id="{}"> <b>{}</b> ({}) <br> {} </li>'.format( 'PB6', titulo_PB6, nPB6, lista_PB6)
        s += u'</ul>'


        self.salvarPagina("membro-" + membro.idLattes + self.extensaoPagina, s)


    def gerar_lista_de_producoes_de_membro (self, lista, titulo):
        s = '<ol>'
        for publicacao in lista:
            s += '<li>' + publicacao.html(self.grupo.listaDeMembros)
        s += '</ol><br>'
        return (len(lista), s, titulo)


    def gerar_lista_de_colaboracoes (self, membro, titulo):
        s = '<ol>'
        detalhe = '<ul>'

        colaboradores = self.grupo.colaboradores_endogenos[membro.idMembro]
        for (idColaborador, quantidade) in sorted(colaboradores, key=lambda x:(-x[1],x[0])):
            colaborador = self.grupo.listaDeMembros[idColaborador]
            s       += u'<li><a href="#{0}">{1}</a> ({2})'.format(colaborador.idLattes, colaborador.nomeCompleto, quantidade)
            detalhe += u'<li id="{0}"> <b>{3} &hArr; <a href="membro-{0}{4}">{1}</a></b> ({2}) <ol>'.format(colaborador.idLattes, colaborador.nomeCompleto, quantidade, membro.nomeCompleto, self.extensaoPagina)

            for publicacao in self.grupo.listaDeColaboracoes[membro.idMembro][idColaborador]:
                detalhe +=  '<li>' + publicacao.html(self.grupo.listaDeMembros)

            detalhe += u'</ol><br>'
        s += '</ol><br>'

        detalhe += '</ul><br>'
        return ( len(colaboradores), s, titulo, detalhe)


    @staticmethod
    def producao_qualis_por_membro(lista_de_membros):
        # FIXME: ver um local melhor para este método

        producao_por_membro = pandas.DataFrame(columns=list(membro.Membro.tabela_qualis.columns) + ['membro'])

        for m in lista_de_membros:
            nome_membro = unicodedata.normalize('NFKD', m.nomeCompleto).encode('ASCII', 'ignore')
            df = pandas.DataFrame({'membro': [nome_membro] * len(m.tabela_qualis)}, index=m.tabela_qualis.index)
            producao_por_membro = producao_por_membro.append(m.tabela_qualis.join(df), ignore_index=True)

        if producao_por_membro.empty:
            producao_por_membro_pivo = pandas.DataFrame()
        else:
            producao_por_membro_pivo = producao_por_membro.pivot_table(values='freq',
                                                                       columns=['ano', 'estrato'],
                                                                       index=['area', 'membro'],
                                                                       dropna=True, fill_value=0, margins=False,
                                                                       aggfunc=sum)
        return producao_por_membro_pivo

    def gerar_pagina_de_producao_qualificado_por_membro(self):
        html = self.pagina_top()
        html += u'<h3>Produção qualificado por área e membro</h3>'
        table_template = u'<table id="producao_por_membro" class="display nowrap">' \
                         u'  <thead>{head}</thead>' \
                         u'  <tfoot>{foot}</tfoot>' \
                         u'  <tbody>{body}</tbody>' \
                         u'</table>'
        table_line_template = u'<tr>{line}</tr>'

        first_column_template = u'<td style="{extra_style}">{header}</td>'
        header_template = u'<th colspan="{colspan}" {extra_pars}>{header}</th>'
        cell_template = u'<td class="dt-body-center">{value}</td>'
        # first_column_template = u'<td style="border: 1px solid black; border-collapse: collapse; background:#CCC;' \
        #                         u'vertical-align: middle; padding: 4px 0; {extra_style}">{header}</td>'
        # header_template = u'<th colspan="{colspan}" style="border-style: solid; border-color: black;' \
        #                   u'border-width: 1 1 1 0; border-collapse: collapse; margin-left:0px; margin-top:0px;' \
        #                   u'background:#CCC; text-align: center; vertical-align: middle; padding: 4px 0;">{header}</th>'
        # cell_template = u'<td style="border-style: solid; border-color: black;' \
        #                 u'border-width: 1 1 1 0; border-collapse: collapse; margin-left:0px; margin-top:0px;' \
        #                 u'background:#EAEAEA; text-align: center; vertical-align: middle; padding: 4px 0;">{value}</td>'

        header_area = header_template.format(header=u'Área', colspan=1, extra_pars='rowspan="2"')
        # header_membro = header_template.format(header=u'Membro', colspan=1)
        header_anos = header_template.format(header='Ano', colspan=1, extra_pars='')
        header_estratos = header_template.format(header=u'Membro \\ Estrato', colspan=1, extra_pars='')

        footer = u'<th>Área</th><th>Membro</th>'

        producao_por_membro = self.producao_qualis_por_membro(self.grupo.listaDeMembros)

        if producao_por_membro.empty:

            self.salvarPagina("producao_membros" + self.extensaoPagina, html)
            return

        anos = sorted(producao_por_membro.columns.get_level_values('ano').unique())
        estratos = sorted(producao_por_membro.columns.get_level_values('estrato').unique())

        for ano in anos:
            header_anos += header_template.format(header=int(ano), colspan=len(estratos), extra_pars='')
            for estrato in estratos:
                header_estratos += header_template.format(header=estrato, colspan=1, extra_pars='')
                footer += '<th style="display: ;"></th>'

        first_row_header = table_line_template.format(line=header_area + header_anos)
        second_row_header = table_line_template.format(line=header_estratos)
        # header = header_area + header_membro + header_estratos
        table_header = first_row_header + second_row_header

        table_footer = table_line_template.format(line=footer)

        areas = sorted(producao_por_membro.index.get_level_values('area').unique())
        membros = sorted(producao_por_membro.index.get_level_values('membro').unique())

        lines = u''
        for area in areas:
            line_area = first_column_template.format(header=area, extra_style='')
            for membro in membros:
                line = line_area
                line += cell_template.format(value=membro)
                for ano in anos:
                    for estrato in estratos:
                        try:
                            freq = producao_por_membro.ix[area, membro][ano, estrato]
                            line += cell_template.format(value=freq if freq else '&nbsp;')  # não mostrar zeros ou nulos
                        except KeyError:
                            line += cell_template.format(value='&nbsp;')
                lines += table_line_template.format(line=line)

        table = table_template.format(head=table_header, body=lines, foot=table_footer)

        html += table

        html += '''<script>
                  $(document).ready( function () {
                      var lastIdx = null;
                      var table = $("#producao_por_membro").DataTable({
                          "dom": 'C<"clear">lfrtip',
                          scrollX: true,
                          //scrollY: "400px",
                          //scrollCollapse: true,
                          paging: true,
                          stateSave: true,
                          initComplete: function () {
                              var api = this.api();
                              api.columns().indexes().flatten().each( function ( i ) {
                                  var column = api.column( i );
                                  var select = $('<select><option value=""></option></select>')
                                      .appendTo( $(column.footer()).empty() )
                                      .on( 'change', function () {
                                          var val = $.fn.dataTable.util.escapeRegex(
                                              $(this).val()
                                          );
                                          console.log(val);
                                          column
                                              .search( val ? '^'+val+'$' : '', true, false )
                                              .draw();
                                      } );
                                  column.data().unique().sort().each( function ( d, j ) {
                                      select.append( '<option value="'+d+'">'+d+'</option>' )
                                  } );
                              } );
                          },
                      });
                      $('#producao_por_membro tbody')
                              .on( 'mouseover', 'td', function () {
                                  var colIdx = table.cell(this).index().column;
                                  if ( colIdx !== lastIdx ) {
                                        $( table.cells().nodes() ).removeClass( 'highlight' );
                                        $( table.column( colIdx ).nodes() ).addClass( 'highlight' );
                                  }
                              } )
                              .on( 'mouseleave', function () {
                                  $( table.cells().nodes() ).removeClass( 'highlight' );
                              } );
                  });
                </script>'''
        # '      .rowGrouping({' \
        # '        iGroupingColumnIndex: 1,' \
        # '        sGroupingColumnSortDirection: "asc",' \
        # '        bExpandableGrouping: true,' \
        # '        bExpandSingleGroup: true,' \
        # '        });' \

        # Salvar em planilha
        xls_filename = os.path.join(self.dir, 'producao_membros.xls')
        producao_por_membro.to_excel(os.path.abspath(xls_filename))
        html += '<a href="{}">{}</a>'.format(os.path.abspath(xls_filename), 'Baixar planilha com os dados')


        self.salvarPagina("producao_membros" + self.extensaoPagina, html)

    def pagina_top(self, cabecalho=''):
        nome_grupo = self.grupo.obterParametro('global-nome_do_grupo').decode("utf8")

        s = self.html1
        template = u'<head>' \
                   '<meta http-equiv="Content-Type" content="text/html; charset=utf8">' \
                   '<meta name="Generator" content="scriptLattes">' \
                   '<title>{nome_grupo}</title>' \
                   '<link rel="stylesheet" href="css/scriptLattes.css" type="text/css">' \
                   '<link rel="stylesheet" type="text/css" href="css/jquery.dataTables.css">' \
                   '<link rel="stylesheet" type="text/css" href="css/dataTables.colVis.min.css">' \
                   '<script type="text/javascript" charset="utf8" src="js/jquery.min.js"></script>' \
                   '<script type="text/javascript" charset="utf8" src="js/jquery.dataTables.min.js"></script>' \
                   '<script type="text/javascript" charset="utf8" src="js/dataTables.colVis.min.js"></script>' \
				   '<script src="http://professor.ufabc.edu.br/~jesus.mena/sorttable.js"></script>'\
                   '{cabecalho}' \
                   '</head>' \
                   '<body><div id="header2"> <button onClick="history.go(-1)">Voltar</button>' \
                   '<h2>{nome_grupo}</h2></div>'
        # '<script type="text/javascript" charset="utf8" src="jquery.dataTables.rowGrouping.js"></script>' \
        s += template.format(nome_grupo=nome_grupo, cabecalho=cabecalho)
        return s




    def salvarPagina(self, nome, conteudo):
        file = open(os.path.join(self.dir, nome), 'w')
        file.write(conteudo.encode('utf8', 'replace'))
        file.close()


    def salvarPublicacaoEmFormatoRIS(self, pub):
        self.arquivoRis.write(pub.ris().encode('utf8'))



def menuHTMLdeBuscaPB(titulo):
    titulo = re.sub('\s+', '+', titulo)

    s = '<br>\
         <font size=-1> \
         [ <a href="http://scholar.google.com/scholar?hl=en&lr=&q=' + titulo + '&btnG=Search">cita&ccedil;&otilde;es Google Scholar</a> | \
           <a href="http://academic.research.microsoft.com/Search?query=' + titulo + '">cita&ccedil;&otilde;es Microsoft Acad&ecirc;mico</a> | \
           <a href="http://www.google.com/search?btnG=Google+Search&q=' + titulo + '">busca Google</a> ] \
         </font><br>'
    return s


def menuHTMLdeBuscaPT(titulo):
    titulo = re.sub('\s+', '+', titulo)

    s = '<br>\
         <font size=-1> \
         [ <a href="http://www.google.com/search?btnG=Google+Search&q=' + titulo + '">busca Google</a> | \
           <a href="http://www.bing.com/search?q=' + titulo + '">busca Bing</a> ] \
         </font><br>'
    return s


def menuHTMLdeBuscaPA(titulo):
    titulo = re.sub('\s+', '+', titulo)

    s = '<br>\
         <font size=-1> \
         [ <a href="http://www.google.com/search?btnG=Google+Search&q=' + titulo + '">busca Google</a> | \
           <a href="http://www.bing.com/search?q=' + titulo + '">busca Bing</a> ] \
         </font><br>'
    return s


def formata_qualis(qualis, qualissimilar):
    s = ''
    if not qualis==None:
        if qualis=='':
            qualis = 'Qualis nao identificado'

        if qualis=='Qualis nao identificado':
            # Qualis nao identificado - imprime em vermelho
            s += '<font color="#FDD7E4"><b>Qualis: N&atilde;o identificado</b></font> ('+qualissimilar+')'
        else:
            if qualissimilar=='':
                # Casamento perfeito - imprime em verde
                s += '<font color="#254117"><b>Qualis: ' + qualis + '</b></font>'
            else:
                # Similar - imprime em laranja
                s += '<font color="#F88017"><b>Qualis: ' + qualis + '</b></font> ('+qualissimilar+')'
    return s


'''
def formata_qualis(qualis, qualissimilar):
    s = ''

    if not qualis:
        #s += '<font color="#FDD7E4"><b>Qualis: N&atilde;o identificado</b></font>'
        s += ''
    else:
        s += '<font color="#254117"><b>Qualis: </b></font> '
        if type(qualis) is str:
            s += '<font class="area"><b>SEM_AREA</b></font> - <b>' + qualis + '</b>&nbsp'
        else:
            l = ['<font class="area"><b>' + area + '</b></font> - <b>' + q + '</b>' for area, q in
                 sorted(qualis.items(), key=lambda x: x[0])]
            s += '&nbsp|&nbsp'.join(l)
    return s
'''
